import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL } from './lib/options.js';

export const options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  const res = http.get(`${BASE_URL}/healthz`);

  check(res, {
    'healthz 200': (r) => r.status === 200,
  });

  sleep(1);
}
