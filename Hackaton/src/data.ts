export const BRANCHES = [
  { id: 1, name: 'Sucursal Centro', addr: 'Av. Hidalgo 304, Centro', phone: '449-123-4567', docs: 12, emoji: '🏥', svcs: 'Consulta general · Cardiología · Ginecología' },
  { id: 2, name: 'Sucursal Norte', addr: 'Blvd. L.D. Colosio 1200', phone: '449-987-6543', docs: 8, emoji: '🏨', svcs: 'Pediatría · Traumatología · Radiología' },
  { id: 3, name: 'Sucursal Sur', addr: 'Av. Aguascalientes Sur 502', phone: '449-456-7890', docs: 10, emoji: '🏩', svcs: 'Neurología · Dermatología · Urgencias 24h' },
  { id: 4, name: 'Sucursal Oriente', addr: 'C. Venustiano Carranza 88', phone: '449-321-0987', docs: 6, emoji: '🏪', svcs: 'Medicina general · Oftalmología · Laboratorio' },
  { id: 5, name: 'Sucursal Pátzcuaro', addr: 'Calle Real 15, Las Flores', phone: '449-654-3210', docs: 7, emoji: '🏦', svcs: 'Consulta general · Ultrasonido · Nutrición' },
  { id: 6, name: 'Sucursal Ojocaliente', addr: 'Carretera 45 Km 12', phone: '449-111-2233', docs: 5, emoji: '🏢', svcs: 'Medicina familiar · Ginecología · Rayos X' },
];

export const SPECS = [
  'Medicina general',
  'Cardiología',
  'Pediatría',
  'Ginecología',
  'Traumatología',
  'Neurología',
  'Dermatología',
  'Oftalmología',
  'Nutrición',
];

export const HOURS = [
  '07:00', '07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
  '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30',
  '17:00', '17:30', '18:00',
];

export const CONSULT = ['101', '102', '203', '204', '301', '305', '402'];

export const ST = {
  confirmed: { label: 'Confirmada', cls: 'badge-ok', stripe: 's-ok' },
  pending: { label: 'Pendiente', cls: 'badge-pend', stripe: 's-pend' },
  cancelled: { label: 'Cancelada', cls: 'badge-cancel', stripe: 's-cancel' },
  delayed: { label: 'Adelantada', cls: 'badge-ahead', stripe: 's-ahead' },
} as const;
