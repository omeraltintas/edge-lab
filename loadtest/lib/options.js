// Tum senaryolarin ortak ayarlari.
export const BASE_URL = __ENV.BASE_URL || 'http://192.168.56.10:18000';

// Baseline icin esikler gevsek: once olcmek, sonra kapi koymak istiyoruz.
export const thresholds = {
  http_req_failed: ['rate<0.001'],
  http_req_duration: ['p(95)<100'],
};

// p95/p99 olcmek icin varsayilan trend istatistikleri yetmiyor.
export const summaryTrendStats = ['avg', 'min', 'med', 'p(90)', 'p(95)', 'p(99)', 'max'];

export function seedCode() {
  const n = Math.floor(Math.random() * 1000);
  return `seed${String(n).padStart(3, '0')}`;
}
