# 0003 — Kong'u DB-less ve "geçiş" modunda öne koymak

## Bağlam

Faz 1'de üç replica ve HAProxy var; kapasite 43 → 103 rps. Faz 2'nin sorusu
gateway katmanı: kimlik, kota, rate limit gibi politikalar uygulamanın içine
gömülmeden nereye konur?

İki karar birbirine karışıyor:

1. Gateway olarak ne kullanılacak?
2. Gateway açılır açılmaz plugin'ler de açılacak mı?

## Karar

**Kong 3.9, DB-less modda, HAProxy'nin önüne** konur. HAProxy kaldırılmaz.

Faz 2a'da **hiç plugin yok**: Kong yalnızca isteği HAProxy'ye geçirir. Rate
limit Faz 2b'de, aynı rota üzerine eklenir.

## Gerekçe

- **Ayrı sorular ayrı ölçülür.** Gateway + rate limit'i birlikte açsak, Faz 1'e
  göre farkın ne kadarı "bir katman daha" ne kadarı "her istekte sayaç
  güncellemek" olduğunu ayıramazdık. Geçiş modu, gateway'in saf maliyetini
  verir; plugin farkı sonra bu tabanın üstüne biner.
- **DB-less.** Kong'un kendi Postgres'i, tek VM'de ölçülen sisteme ikinci bir
  veritabanı yükü ekler ve Faz 1'deki "paylaşılan DB darboğazı" ihtimalini
  daha da bulanıklaştırır. Rota tanımı `deploy/kong/kong.yml` dosyasında,
  git'te versiyonlu.
- **HAProxy kalır.** `leastconn`, sağlık kontrolü ve `timeout queue` Faz 1'de
  ölçüldü ve çalışıyor. Kong'u LB'nin yerine koymak iki değişkeni birden
  değiştirmek olurdu. Kong politika, HAProxy dağıtım işi yapar.
- **`:18090` teşhis kapısı.** HAProxy hâlâ host'a açık. "Yavaşlık gateway'de
  mi" sorusu, aynı isteği iki porttan atıp iki sayı görmekle çözülür.

## Bedeli

- Bir katman daha: her istek ekstra bir ağ sıçraması ve bir nginx turu öder.
  Bu tam olarak ölçmek istediğimiz maliyet.
- CPU bütçesi 3.5/4.0 vCPU'ya çıkar (app 1.5 + postgres 1.0 + haproxy 0.5 +
  kong 0.5). Kötü bir komşu eklemek tüm tabloyu bozabilir.
- Kong upstream adresini açılışta çözer. HAProxy yeniden başlayıp IP
  değiştirirse Kong eski adrese gitmeye devam edebilir; Faz 5'teki kill
  testlerinde bu davranışın ele alınması gerekecek.
- Yönetim için ikinci bir port (18081) ve ayrı bir yapılandırma dili var.

## Alternatifler

- **Traefik / Envoy / NGINX**: hepsi çalışırdı. Kong seçildi çünkü rate limit,
  key-auth gibi politikalar plugin olarak hazır; mülakatta "gateway" deyince
  akla gelen ilk ürün ve DB-less modu tek dosyayla kuruluyor.
- **Kong + veritabanı**: Faz 2 için gereğinden ağır; konfigürasyonun git'te
  dosya olarak durması bu lab'da daha değerli.
- **HAProxy yerine Kong**: iki değişkeni birden değiştirmek; Faz 1 sonucuyla
  karşılaştırma imkânı kaybolurdu.
- **Plugin'leri ilk günden açmak**: ölçümü yorumlanamaz hale getirirdi.
