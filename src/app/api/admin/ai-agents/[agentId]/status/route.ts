import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function PUT(
  request: NextRequest,
  { params }: { params: { agentId: string } }
) {
  try {
    const cookieStore = cookies();
    const token = cookieStore.get("token")?.value;

    if (!token) {
      return NextResponse.json(
        { error: "No authentication token" },
        { status: 401 }
      );
    }

    const body = await request.json();

    // Forward the request to the backend
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

    const response = await fetch(`${backendUrl}/admin/ai-agents/${params.agentId}/status`, {
      method: "PUT",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.text();
      return NextResponse.json(
        { error: errorData || "Failed to update AI agent status" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error("Admin AI agent status API error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
