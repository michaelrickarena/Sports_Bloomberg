import Link from "next/link";

const blogs = [
  {
    slug: "arbitrage",
    title: "Arbitrage Betting Explained",
    description:
      "Discover how to guarantee profits by exploiting price differences between sportsbooks with arbitrage betting.",
  },
  {
    slug: "expected-value",
    title: "Expected Value in Sports Betting",
    description:
      "Master the concept of expected value to make smarter, more profitable sports bets over time.",
  },
  {
    slug: "historical-data",
    title: "Using Historical Data for Better Bets",
    description:
      "Leverage past sports results and trends to inform your betting decisions and gain an edge.",
  },
  {
    slug: "implied-odds",
    title: "Implied Odds: What the Bookmakers Are Telling You",
    description:
      "Learn to interpret betting odds as probabilities and uncover hidden value in the lines.",
  },
  {
    slug: "kelly-criterion",
    title: "The Kelly Criterion: Maximizing Your Bankroll",
    description:
      "Optimize your bet sizes for long-term growth and minimize risk using the Kelly Criterion.",
  },
  {
    slug: "no-vig",
    title: "No-Vig Odds: Removing the Sportsbook Edge",
    description:
      "Calculate true odds by stripping out the bookmaker’s margin to find fair value bets.",
  },
  {
    slug: "z-score",
    title: "Z-Score in Sports Analytics",
    description:
      "Use z-scores to identify statistical outliers and spot meaningful trends in sports data.",
  },
  {
    slug: "affordable-analytics",
    title:
      "How Affordable Analytics Tools Are Changing the Way Fans Enjoy Sports",
    description:
      "Explore how accessible analytics tools empower fans to analyze games and make informed decisions.",
  },
  {
    slug: "understanding-odds",
    title:
      "Understanding Sports Odds: A Beginner’s Guide to Reading and Comparing Lines",
    description:
      "Get a clear introduction to reading, interpreting, and comparing sports betting odds.",
  },
  {
    slug: "betting-mistakes",
    title:
      "Top 5 Common Mistakes Fans Make When Analyzing Sports Data (And How to Avoid Them)",
    description:
      "Avoid the most frequent pitfalls in sports data analysis with these practical tips.",
  },
];

export default function BlogHome() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-center">
        Sports Analytics Blog
      </h1>
      <p className="mb-8 text-center text-gray-600 max-w-2xl mx-auto">
        Explore our collection of in-depth articles on sports betting,
        analytics, and strategy. Click any card to read the full post.
      </p>
      <div className="grid gap-6 md:grid-cols-2">
        {blogs.map((blog) => (
          <div
            key={blog.slug}
            className="bg-white rounded-lg shadow p-6 flex flex-col justify-between border border-gray-100 hover:shadow-lg transition"
          >
            <div>
              <h2 className="text-xl font-semibold mb-2">{blog.title}</h2>
              <p className="text-gray-700 mb-4">{blog.description}</p>
            </div>
            <Link
              href={`/blogs/${blog.slug}`}
              className="text-blue-600 font-medium hover:underline self-start mt-auto"
            >
              Read More →
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
