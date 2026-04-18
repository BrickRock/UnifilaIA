import { HOURS, CONSULT } from './data';

export function makeJWT(payload: any) {
  const a = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const b = btoa(JSON.stringify(payload));
  const c = btoa('mc-' + payload.curp);
  return a + '.' + b + '.' + c;
}

export function readJWT(tok: string) {
  try {
    return JSON.parse(atob(tok.split('.')[1]));
  } catch {
    return null;
  }
}

export function getSlots(dateStr: string, branchId: number) {
  const seed = parseInt(dateStr.replace(/-/g, '')) + branchId * 31;
  const rng = (n: number) => ((Math.sin(seed + n * 7.3) * 43758.5453) % 1 + 1) % 1;
  return HOURS.map((t, i) => {
    const busy = rng(i) < 0.40;
    const con = CONSULT[Math.floor(rng(i + 50) * CONSULT.length)];
    return { time: t, consultory: con, busy };
  });
}

export function nextFreeDay(fromDate: string, branchId: number) {
  for (let d = 1; d <= 14; d++) {
    const dt = new Date(fromDate);
    dt.setDate(dt.getDate() + d);
    const ds = dt.toISOString().split('T')[0];
    const s = getSlots(ds, branchId);
    if (s.some(x => !x.busy)) return { date: ds, slots: s };
  }
  return null;
}

export function demoAppts() {
  return [
    { id: 1, spec: 'Cardiología', date: '2025-06-10', time: '10:00', consultory: '204', status: 'confirmed', branch: 'Sucursal Centro', note: '' },
    { id: 2, spec: 'Pediatría', date: '2025-06-15', time: '09:00', consultory: '101', status: 'delayed', branch: 'Sucursal Norte', note: 'Se adelantó de las 09:30' },
    { id: 3, spec: 'Dermatología', date: '2025-05-28', time: '11:00', consultory: '305', status: 'cancelled', branch: 'Sucursal Sur', note: 'Médico canceló por emergencia' },
  ];
}
