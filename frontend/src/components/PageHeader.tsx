export default function PageHeader({ icon: Icon, title, description }: { icon: any; title: string; description?: string }) {
  return (
    <div className="text-center mb-10">
      {Icon && <Icon className="w-10 h-10 text-blue-500 mx-auto mb-3" />}
      <h1 className="text-3xl font-bold text-gray-900 mb-2">{title}</h1>
      {description && <p className="text-gray-500 max-w-xl mx-auto">{description}</p>}
    </div>
  );
}
