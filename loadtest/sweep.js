import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, seedCode, summaryTrendStats } from './lib/options.js';

// Kapali cevrim (closed-loop): sabit sayida sanal kullanici, dusunme suresi yok.
// Amac "kac eszamanli kullanicida gecikme kiriliyor" sorusunu cevaplamak.
// Tek kosuda tek seviye; seviyeleri run-sweep.ps1 dolasiyor.

const VUS = Number(__ENV.VUS || 10);
const DURATION = __ENV.DURATION || '30s';

export const options = {
  vus: VUS,
  duration: DURATION,
  summaryTrendStats,
  // Kesif kosusu: esik yok. Esik Faz 6'da CI'a girecek.
  thresholds: {},
};

export default function () {
  const res = http.get(`${BASE_URL}/${seedCode()}`, { redirects: 0 });

  check(res, {
    '302': (r) => r.status === 302,
  });
}
