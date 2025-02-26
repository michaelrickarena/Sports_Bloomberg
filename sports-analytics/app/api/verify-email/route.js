import { NextResponse } from "next/server";

export async function POST(req) {
  const { token } = await req.json();

  try {
    // Verify token with your Django API (adjust URL as needed)
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/verify-email/`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token }),
      }
    );

    if (response.ok) {
      return NextResponse.json({ message: "Email verified successfully!" });
    } else {
      return NextResponse.json(
        { error: "Email verification failed" },
        { status: 400 }
      );
    }
  } catch (error) {
    console.error("Verification error:", error);
    return NextResponse.json(
      { error: "Something went wrong" },
      { status: 500 }
    );
  }
}
