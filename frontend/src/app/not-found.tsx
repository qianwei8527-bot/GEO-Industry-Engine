import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4 text-center">
      <div className="text-6xl font-bold text-gray-200 mb-4">404</div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">{'页面不存在'}</h1>
      <p className="text-gray-500 mb-8 max-w-md">{'请检查网址是否正确，或返回主页。'}</p>
      <Link href="/" className="bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700">{'返回主页'}</Link>
    </div>
  );
}
