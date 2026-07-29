export default function LoadingSpinner({ size = "md", text = "" }: { size?: "sm" | "md" | "lg"; text?: string }) {
  const sizes = { sm: "w-5 h-5", md: "w-8 h-8", lg: "w-12 h-12" };
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className={'animate-spin rounded-full border-4 border-gray-200 border-t-blue-500 ' + sizes[size]} />
      {text && <p className="mt-3 text-sm text-gray-400">{text}</p>}
    </div>
  );
}
