// Placeholder home page for the DevOps scaffold. Frontend Developer replaces
// this with the real homepage (FE-02) once BE-04 / BE-06 APIs are live.
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8 text-center">
      <h1 className="text-3xl font-bold text-orange-700">
        Simhastha 2028 &mdash; Ujjain Digital Experience Platform
      </h1>
      <p className="text-gray-600">
        Sprint 1 scaffold is running. Real pages are built in the next
        development phase.
      </p>
      <p className="text-sm text-gray-400">
        API base URL: {process.env.NEXT_PUBLIC_API_URL ?? "not set"}
      </p>
    </main>
  );
}
