import Link from "next/link";
import Navigation from "@/components/Navigation";

const blogPosts = [
  {
    title: "How AI is Revolutionizing Customer Service",
    excerpt: "Discover how AI-powered chat systems are transforming customer interactions and improving satisfaction rates.",
    date: "2024-01-15",
    readTime: "5 min read",
    category: "AI Trends",
    slug: "how-ai-is-revolutionizing-customer-service"
  },
  {
    title: "Getting Started with Custom AI Models",
    excerpt: "A comprehensive guide to training your own AI models for personalized conversations and better results.",
    date: "2024-01-10",
    readTime: "8 min read",
    category: "Tutorial",
    slug: "getting-started-with-custom-ai-models"
  },
  {
    title: "Voice AI: The Future of Human-Computer Interaction",
    excerpt: "Exploring the latest advancements in voice recognition and synthesis technology.",
    date: "2024-01-05",
    readTime: "6 min read",
    category: "Technology",
    slug: "voice-ai-the-future-of-human-computer-interaction"
  },
  {
    title: "Security Best Practices for AI Chat Platforms",
    excerpt: "Learn how to protect your data and ensure privacy when using AI-powered communication tools.",
    date: "2024-01-01",
    readTime: "7 min read",
    category: "Security",
    slug: "security-best-practices-for-ai-chat-platforms"
  }
];

export default function BlogPage() {
  return (
    <div className="min-h-screen bg-white">
      <Navigation />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Blog & Insights
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Stay informed with the latest trends, tutorials, and insights about AI-powered communication.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {blogPosts.map((post, index) => (
            <article key={index} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
              <div className="mb-3">
                <span className="inline-block bg-blue-100 text-blue-800 text-sm font-semibold px-3 py-1 rounded-full">
                  {post.category}
                </span>
              </div>
              <h2 className="text-xl font-bold text-gray-900 mb-3 hover:text-blue-600 transition-colors">
                <Link href={`/blog/${post.slug}`}>
                  {post.title}
                </Link>
              </h2>
              <p className="text-gray-600 mb-4">{post.excerpt}</p>
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>{new Date(post.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                <span>{post.readTime}</span>
              </div>
            </article>
          ))}
        </div>

        <div className="text-center mt-12">
          <Link
            href="/"
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
