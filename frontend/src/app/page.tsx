import Link from 'next/link';
import ExampleEntry from '../slices/example/ExampleEntry';

export default function Home() {
  return (
    <section>
      <h1>Conductor Frontend Skeleton</h1>
      <p>
        This is a minimal Next.js App Router project structured around vertical slices. Each slice is
        self-contained and communicates through explicit contracts.
      </p>
      <div style={{ marginBottom: '1rem' }}>
        <Link href="/demo/status">Visit the demo status slice</Link>
      </div>
      <ExampleEntry />
      <div style={{ marginTop: '1.5rem' }}>
        <Link href="https://nextjs.org/docs/app" target="_blank">
          Explore Next.js App Router docs
        </Link>
      </div>
    </section>
  );
}
