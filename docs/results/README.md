# Ölçüm kayıtları

Her `.json` dosyası bir k6 `--summary-export` çıktısıdır. Tablodaki bir sayının
nereden geldiğini görmek için dosya adına bak. Ham dosya yoksa sayı yok sayılır.

## Ortam künyesi

| Alan | Değer |
|---|---|
| Ölçülen sistem | Tek VM (VirtualBox, 192.168.56.10), 4 vCPU |
| Sanallaştırma | Donanım hızlandırma yok (NEM yazılım emülasyonu) |
| Yük üretici | Windows host, k6 (VM'in dışında) |
| Uygulama | FastAPI + SQLAlchemy 2.0, tek uvicorn worker, Python 3.12 |
| Veritabanı | Postgres 17-alpine, tek instance |
| CPU bütçesi | app 0.5 vCPU/replica, postgres 1.0, haproxy 0.5, kong 0.5 |

Mutlak sayılar bu kutu için düşüktür: emülasyonlu VM'de tek bir redirect
~10 ms CPU yiyor. Projedeki bütün iddialar **aynı kutu üzerindeki farklar**
üzerinden kuruludur, "saniyede X istek" mutlak değeri üzerinden değil.

Ortak yük profili: `loadtest/sweep.js`, kapalı çevrim, düşünme süresi yok,
30 saniye, rastgele `seed000..seed999` kodu, `GET /{code}` beklenen 302.

## Faz 0 — tek replica, doğrudan (0.5 vCPU)

| VU | Dosya | rps | medyan | p95 | 5xx |
|---|---|---|---|---|---|
| 5 | `sweep-vus-5.json` | 50.0 | 95 ms | 192 ms | 0 |
| 10 | `sweep-vus-10.json` | 33.3 | 203 ms | 395 ms | 0 |
| 20 | `sweep-vus-20.json` | 43.3 | 407 ms | 903 ms | 0 |
| 40 | `sweep-vus-40.json` | 42.8 | 881 ms | 2101 ms | 0 |
| 80 | `sweep-vus-80.json` | 43.1 | 1702 ms | 3077 ms | 0 |
| 160 | `sweep-vus-160.json` | 34.6 | 3588 ms | 11546 ms | 0 |

Kapasite **~43 rps**. 20 VU'dan sonra rps sabit, gecikme doğrusal artıyor:
kuyruk. 10 VU'daki düşüş connection pool ısınmasına yorumlandı.

Açık çevrim (`step-run1.json`): 30.9 rps, medyan 1865 ms, 21884 düşen istek.
Aşırı yük koşusu (`overload-500rps-run1.json`): 500 rps teklif, 33 rps
karşılandı, medyan 15.3 s, 5xx sıfır.

## Faz 1 — 3 replica + HAProxy (1.5 vCPU app)

| VU | Dosya | rps | medyan | p95 | p99 | 5xx |
|---|---|---|---|---|---|---|
| 5 | `faz1-sweep-vus-5.json` * | 83.1 | 17 ms | 63 ms | 102 ms | 0 |
| 20 | `faz1-sweep-vus-20.json` * | 79.0 | 99 ms | 263 ms | 468 ms | 0 |
| 40 | `faz1-sweep-vus-40.json` | **102.6** | 218 ms | 626 ms | 7.3 s | 0 |
| 80 | `faz1-sweep-vus-80.json` | **103.4** | 509 ms | 1374 ms | 8.2 s | 0 |

\* 5 ve 20 VU koşuları 30 saniyede bitmedi (58.6 s / 54.3 s): içlerinde 30
saniyelik asılı istek var, k6 `gracefulStop` boyunca bekledi. Bu iki satırın
rps'i kapasite göstergesi değildir; yalnızca "boşta medyan 17 ms" bilgisini
verirler.

Kapasite **~103 rps**: 40 ve 80 VU'da rps aynı, gecikme iki katı.
Little yasası doğrulaması: 40 VU ÷ 0.388 s = 103; 80 VU ÷ 0.767 s = 104.

Açık çevrim (`faz1-step-run1.json`): 26962 istek, ortalama 74.9 rps, 6037
düşen. Ortalamanın düşük olması rampanın düşük kademelerini de içermesinden;
kapasite kapalı çevrimden okunur.

## Faz 0 → Faz 1

| | Faz 0 | Faz 1 | |
|---|---|---|---|
| Kapasite | 43 rps | 103 rps | 2.4× |
| CPU bütçesi (app) | 0.5 | 1.5 | 3.0× |
| vCPU başına | 86 rps | 69 rps | −20% |
| 40 VU medyan | 881 ms | 218 ms | 4× iyi |
| 80 VU medyan | 1702 ms | 509 ms | 3.3× iyi |

Lineer 3× beklenirken 2.4× çıktı ve vCPU başına verim düştü. En olası sebep
paylaşılan Postgres (1.0 vCPU): 43 rps'te ~0.42 çekirdek kullanırken 103 rps'te
tavanına dayanıyor. **Bu doğrulanmadı**; kayda böyle geçiyor.

Ayrıca p99'un p95'ten kopması (626 ms → 7.3 s) tek tek yavaş istekler değil,
~30 isteğin birlikte takılıp birlikte bitmesi. Tüm fazlalık `http_req_waiting`
içinde, yani sunucu tarafında. Sebep tespit edilmedi.

## Kurallar

- Kapasite **kapalı çevrim** eğrisinden okunur (rps sabitlenip gecikme artan
  nokta). Açık çevrimde kuyruk kapasiteyi olduğundan yüksek gösterebilir.
- Tek koşu kaydedilir. İki koşu arasında %20'den fazla fark çıkarsa önce
  ortam sorgulanır, sonra sayı yazılır.
- 5xx sıfır olması "başarı" değil, "çökmüyor" demektir; kapasite ayrı ölçülür.
