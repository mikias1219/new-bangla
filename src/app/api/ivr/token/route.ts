import { NextRequest, NextResponse } from "next/server";
import jwt from "jsonwebtoken";
import { getServerSession } from "next-auth";

export async function GET(request: NextRequest) {
  try {
    // Verify user authentication
    const session = await getServerSession();
    if (!session) {
      return NextResponse.json(
        { error: "Authentication required" },
        { status: 401 }
      );
    }

    // Get Twilio credentials from environment
    const twilioAccountSid = process.env.TWILIO_ACCOUNT_SID;
    const twilioApiKey = process.env.TWILIO_API_KEY;
    const twilioApiSecret = process.env.TWILIO_API_SECRET;
    const twilioApplicationSid = process.env.TWILIO_APPLICATION_SID;

    if (!twilioAccountSid || !twilioApiKey || !twilioApiSecret || !twilioApplicationSid) {
      return NextResponse.json(
        { error: "Twilio not configured" },
        { status: 500 }
      );
    }

    // Create JWT token for Twilio Device
    const now = Math.floor(Date.now() / 1000);
    const payload = {
      iss: twilioApiKey,
      sub: twilioAccountSid,
      exp: now + 3600, // 1 hour
      grants: {
        identity: session.user?.email || "user",
        voice: {
          application_sid: twilioApplicationSid,
        },
      },
    };

    const token = jwt.sign(payload, twilioApiSecret, {
      header: {
        alg: "HS256",
        typ: "JWT",
        cty: "twilio-fpa;v=1",
      },
    });

    return NextResponse.json({ token });

  } catch (error) {
    console.error("Error generating Twilio token:", error);
    return NextResponse.json(
      { error: "Failed to generate token" },
      { status: 500 }
    );
  }
}
