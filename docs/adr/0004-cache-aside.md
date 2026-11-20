# 0004 — Cache-aside, Redis, fail-open

## Bağlam

`GET /{code}` trafiğin neredeyse tamamı ve her istek tek bir satır okuyor:
`SELECT ... FROM links WHERE code = ?`. Faz 1'de replica sayısını 3'e çıkarınca
kapasite 3× değil 2.4× arttı; şüpheli olan paylaşılan Postgres'ti (1.0 vCPU).
Okuma yoluna bir cache koymak hem gecikmeyi hem DB yükünü düşürmeli.

## Karar

**Cache-aside (lazy loading)**, Redis'te, 300 saniye TTL, **fail-open**.
Anahtar `link:{code}`, değer hedef URL. `DELETE` başarılı olunca anahtar silinir.
`CACHE_ENABLED` ortam değişkeni cache'i tamamen kapatır (A/B için).

## Gerekçe

- **Cache-aside**, okuma ağırlıklı iş için en az hareketli parçalı desen: DB
  tek doğruluk kaynağı kalır, cache sadece hızlandırır. Cache silinirse sistem
  yavaşlar, yanlış cevap vermez.
- **Redis, in-process dict değil.** Üç replica var: app-2'deki `DELETE`,
  app-1'in belleğindeki kopyayı silemez. Paylaşılan cache, invalidation'ı
  tek bir yere indirir. Bedeli her istekte bir ağ sıçraması.
- **TTL şart.** Invalidation kaçarsa (ağ hatası, yarış) bayat kaydın ömrü
  TTL ile sınırlı. TTL'siz cache, "sildim ama hâlâ gidiyor" hatasının davetiyesi.
- **Fail-open.** Redis yavaşsa 50 ms'de vazgeçip DB'ye düşeriz. Cache'in işi
  hızlandırmak; çöktüğünde sistemi çökertmemeli. Bu yüzden `/readyz` Redis'e
  bakmaz: cache arızası üç replica'yı birden havuzdan düşürmemeli.
- **Yazma yolunda cache yok.** `POST` ve `DELETE` DB'ye yazar; cache yalnızca
  okumada devreye girer. Write-through burada fayda sağlamaz, karmaşıklık ekler.

## Bedeli

- **Bayat veri penceresi.** `DELETE` ile DB commit'i arasında geçen sürede
  gelen eşzamanlı bir `GET`, eski URL'i cache'e geri yazabilir. Kayıt en fazla
  TTL kadar yaşar. Klasik cache-aside yarışı; kabul edildi, TTL sınırlıyor.
- **Thundering herd.** Anahtar düştüğünde aynı anda gelen istekler DB'ye
  birlikte gider. Tek kod (ör. `hotlink`) üzerinden yapılan ölçümde bu
  görünür. Çözümü (single-flight / kilit) bu faza alınmadı.
- **Ek ağ sıçraması.** Her istekte bir Redis turu: gecikmeye ~0.5-1 ms.
  Faz 3 ölçümünün ana konusu bu.
- **İki sistem, iki arıza modu.** Redis'in bellek politikası, bağlantı havuzu,
  timeout'ları ayrı ayrı düşünülmeli.

## Alternatifler

- **In-process LRU**: en hızlı (ağ yok) ama üç replica arasında tutarsız;
  invalidation için pub/sub veya yayın mekanizması gerekir. Faz 5'te
  karşılaştırma adayı.
- **Write-through**: yazma gecikmesini artırır, bu lab'da yazma trafiği yok.
- **Negatif cache (404'ler)**: invalidation karmaşıklığını artırır, kazanç
  küçük.
- **Postgres'e yüklenmek** (indeks, shared_buffers, daha çok CPU): bu da bir
  cevap, ama cache katmanının ne kazandırdığını göstermek projenin konusu.
