import type { ReactNode } from 'react';

interface ShellLayoutProps {
  header: ReactNode;
  sidebar: ReactNode;
  main: ReactNode;
  activity: ReactNode;
}

const ShellLayout = ({ header, sidebar, main, activity }: ShellLayoutProps) => {
  return (
    <div className="grid h-screen grid-cols-[260px_1fr_340px] grid-rows-[80px_1fr] bg-brand-accent text-slate-200">
      <header className="col-span-3 border-b border-slate-800 bg-slate-950/60 px-8 py-4 backdrop-blur">
        {header}
      </header>
      <aside className="border-r border-slate-800 px-6 py-6">
        {sidebar}
      </aside>
      <main className="px-8 py-6 overflow-y-auto">
        {main}
      </main>
      <section className="border-l border-slate-800 px-6 py-6 overflow-y-auto">
        {activity}
      </section>
    </div>
  );
};

export default ShellLayout;
