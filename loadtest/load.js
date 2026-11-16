import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, seedCode, summaryTrendStats, thresholds } from './lib/options.js';

// Sabit VU yerine varis hizi: "saniyede kac istek" sorusunun cevabi makineye gore kaymaz.
export const options = {
  scenarios: {
    ramp: {
      executor: 'ramping-arrival-rate',
      startRate: 50,
      timeUnit: '1s',
      preAllocatedVUs: 200,
      maxVUs: 500,
      stages: [
        { target: 50, duration: '30s' },
        { target: 300, duration: '2m' },
        { target: 500, duration: '2m' },
        { target: 0, duration: '30s' },
      ],
    },
  },
  thresholds,
  summaryTrendStats,
};

const HOT_CODE = __ENV.CODE;

export default function () {
  const code = HOT_CODE || seedCode();

  // redirects: 0 - yoksa k6 hedef siteyi olcer, bizi degil.
  const res = http.get(`${BASE_URL}/${code}`, { redirects: 0 });

  check(res, {
    '302': (r) => r.status === 302,
  });
}
