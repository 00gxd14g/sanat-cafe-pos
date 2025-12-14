import qz from 'qz-tray';

type PrintPayload = {
  printerHint?: string;
  encoding?: string;
  raw: string[];
};

let initPromise: Promise<void> | null = null;

async function fetchCert(): Promise<string> {
  const r = await fetch('/api/qz/cert', { credentials: 'include' });
  if (!r.ok) throw new Error('Certificate alınamadı');
  return await r.text();
}

async function sign(toSign: string): Promise<string> {
  const r = await fetch('/api/qz/sign', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ toSign }),
  });
  if (!r.ok) throw new Error('İmza üretilemedi');
  const j = (await r.json()) as { signature?: string };
  if (!j.signature) throw new Error('İmza üretilemedi');
  return j.signature;
}

export function initQZ(): Promise<void> {
  if (initPromise) return initPromise;

  initPromise = (async () => {
    qz.security.setCertificatePromise(fetchCert);
    qz.security.setSignaturePromise((toSign: string) => sign(toSign));

    if (!qz.websocket.isActive()) {
      await qz.websocket.connect();
    }
  })();

  return initPromise;
}

async function ackPrintJob(jobId: number, status: 'SENT' | 'PRINTED' | 'ERROR', error?: string) {
  await fetch(`/api/print/jobs/${jobId}/ack`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, error }),
  }).catch(() => null);
}

export async function printFromJobId(jobId: number): Promise<void> {
  await initQZ();

  const r = await fetch('/api/print/payload', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ printJobId: jobId }),
  });
  if (!r.ok) throw new Error('Baskı payload alınamadı');
  const payload = (await r.json()) as PrintPayload;
  if (!payload?.raw?.length) throw new Error('Baskı payload boş');

  const encoding = payload.encoding || 'CP857';
  try {
    await ackPrintJob(jobId, 'SENT');

    const printerName = payload.printerHint ? await qz.printers.find(payload.printerHint) : await qz.printers.getDefault();
    const cfg = qz.configs.create(printerName, { encoding });
    await qz.print(cfg, payload.raw);

    await ackPrintJob(jobId, 'PRINTED');
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    await ackPrintJob(jobId, 'ERROR', msg);
    throw e;
  }
}
