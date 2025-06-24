export default function ComingSoon() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] py-12">
      <h1 className="text-3xl md:text-4xl font-bold mb-4 text-center">
        Coming Soon
      </h1>
      <p className="text-lg text-gray-600 mb-6 text-center max-w-xl">
        This blog post is currently in progress and will be published soon.
        Check back later for updates!
      </p>
      <span className="text-5xl animate-bounce">🚧</span>
    </div>
  );
}
