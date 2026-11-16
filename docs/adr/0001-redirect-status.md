# 0001 — Kısa link yönlendirmesinde 302

## Bağlam

`GET /{code}` isteği kullanıcıyı hedef URL'e göndermeli. HTTP 301 (kalıcı) ve
302 (geçici) iki doğal aday.

## Karar

**302** kullanıyoruz.

## Gerekçe

- 301 tarayıcıda kalıcı cache'lenir. Aynı kullanıcı ikinci kez tıkladığında istek
  sunucuya hiç gelmez; tıklama analitiği ve link iptali imkânsızlaşır.
- Cache invalidation senaryosu (Faz 3) 301 ile anlamsızlaşır: tarayıcı eski hedefi
  kendi tarafında tutar, biz ne yaparsak yapalım değişmez.
- 302 ile her istek edge'e gelir; rate limit, kota ve cache kararları bizde kalır.

## Bedeli

Her tıklama için sunucu isteği ödenir. Yüksek trafikte bu maliyet CDN/edge cache
ile azaltılır; ama o zaman da analytics için ayrı bir beacon gerekir.

## Alternatifler

- **301**: daha az sunucu yükü, analytics ve iptal kaybı. Ürün gereksinimi
  analitik olduğu için reddedildi.
- **307/308**: metodun korunması burada anlamsız; GET dışı istek beklemiyoruz.

Not: Faz 6'da tarayıcı cache'ini bilinçli açmak istersek `Cache-Control` ile
ayrı bir deney yapılabilir; bu ADR varsayılan davranışı tanımlar.
