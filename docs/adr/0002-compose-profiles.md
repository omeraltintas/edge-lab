# 0002 — Tek compose dosyası, topoloji profilleri

## Bağlam

Projenin amacı aynı uygulamayı farklı topolojilerde ölçmek:

- A: app (tek replica, doğrudan)
- B: HAProxy → 3 app
- C: Kong → HAProxy → 3 app
- D: Caddy → Kong → HAProxy → 3 app

Dört ayrı compose dosyası kopyala-yapıştır ile çoğalır ve zamanla birbirinden
ayrışır.

## Karar

Tek `deploy/compose.yml`, topolojiler `profiles:` ile seçilir. Ölçüm sonuçları
aynı dosyanın hangi profille çalıştığını kaydeder.

```bash
docker compose -f deploy/compose.yml --env-file deploy/.env --profile lb up -d
```

## Gerekçe

- Ortak servisler (postgres, app) tek yerde tanımlı; tek doğruluk kaynağı var.
- Profil farkı, ölçüm farkının tek açıklaması olur.
- Yeni bir katman eklemek dosya çoğaltmaz, servis + profil ekler.

## Bedeli

Compose profilleri "aynı anda tek topoloji" varsayımına uygun; iki topolojiyi aynı
anda çalıştırmak istersen port çakışır. Bu lab için kabul edilebilir: ölçümler
sırayla yapılır.

## Alternatifler

- **Ayrı dosyalar** (`compose.baseline.yml`, `compose.lb.yml`): kopya çoğalması.
- **Kubernetes / Helm**: Faz 0-2 için gereğinden ağır; k3s karşılaştırması Faz 7'de
  opsiyonel.
