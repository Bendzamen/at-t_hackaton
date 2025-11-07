import { type NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Generate a unique projectId (in production, you'd create this in your database)
    const projectId = `proj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    console.log(' Project created with ID:', projectId);

    return NextResponse.json({
      projectId,
      success: true,
    });
  } catch (error) {
    console.error(' Error in /start:', error);
    return NextResponse.json({ error: 'Failed to start project' }, { status: 500 });
  }
}
