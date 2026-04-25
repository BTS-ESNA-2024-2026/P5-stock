import AppLayout from '../layouts/AppLayout'

type PlaceholderPageProps = {
  title: string
  subtitle: string
}

export default function PlaceholderPage({ title, subtitle }: PlaceholderPageProps) {
  return (
    <AppLayout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Module en cours</span>
          <div className="title">{title}</div>
          <div className="subtitle">{subtitle}</div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-title">Migration front-end terminee</div>
        <p className="subtitle mt-1">
          Cette section est maintenant geree par React. Connectez-la aux endpoints API selon les besoins metier.
        </p>
      </section>
    </AppLayout>
  )
}