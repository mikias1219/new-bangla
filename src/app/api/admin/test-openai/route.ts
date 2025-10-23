import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function GET(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const token = cookieStore.get("token")?.value;

    if (!token) {
      return NextResponse.json(
        { error: "No authentication token" },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(request.url);
    const message = searchParams.get('message');

    if (!message) {
      return NextResponse.json(
        { error: "Message parameter is required" },
        { status: 400 }
      );
    }

    // Forward the request to the backend
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

    const response = await fetch(`${backendUrl}/admin/test-openai?message=${encodeURIComponent(message)}`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.text();
      return NextResponse.json(
        { error: errorData || "Failed to test OpenAI" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error("Admin test OpenAI API error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
