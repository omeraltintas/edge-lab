import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, seedCode, summaryTrendStats, thresholds } from './lib/options.js';

// Acik cevrim (open-loop), kademeli: her kademede hedef varis hizi sabit.
// Talep kapasiteyi asarsa gecikme kuyruk yuzunden buyur; bu yuzden maxVUs
// sinirli tutuluyor ve "dropped_iterations > 0" doygunluk sinyali sayiliyor.
//
// Kademe sonunda p95 < 100ms ve dropped_iterations == 0 ise o hiz surdurulebilir.

export const options = {
  scenarios: {
    steps: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 100,
      stages: [
        { target: 10, duration: '30s' },
        { target: 20, duration: '60s' },
        { target: 40, duration: '60s' },
        { target: 80, duration: '60s' },
        { target: 160, duration: '60s' },
        { target: 320, duration: '60s' },
        { target: 0, duration: '30s' },
      ],
    },
  },
  thresholds,
  summaryTrendStats,
};

// Tek bir sicak kodu olcmek icin: -e CODE=hotlink
const HOT_CODE = __ENV.CODE;

export default function () {
  const code = HOT_CODE || seedCode();

  // redirects: 0 - yoksa k6 hedef siteyi olcer, bizi degil.
  const res = http.get(`${BASE_URL}/${code}`, { redirects: 0 });

  check(res, {
    '302': (r) => r.status === 302,
  });
}
