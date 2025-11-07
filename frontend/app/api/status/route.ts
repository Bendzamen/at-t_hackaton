import { type NextRequest, NextResponse } from 'next/server';

interface StatusResponse {
  stage: string;
  message: string;
  zip?: string;
  index: number;
}

// Mock data for different stages
const mockResponses: StatusResponse[] = [
  {
    stage: 'Analyzing',
    message: 'Analyzing your request...',
    index: 0,
  },
  {
    stage: 'Processing',
    message: 'Processing files and generating output...',
    index: 1,
  },
  {
    stage: 'Finalizing',
    message: 'Finalizing the project structure...',
    index: 2,
  },
  {
    stage: 'Complete',
    message: '✅ Your project is ready!',
    index: 3,
    zip: 'data:application/zip;base64,UEsDBBQACAAIAH...',
  },
];

// In-memory store to track project progress (in production, use database)
const projectProgress: Record<string, { currentIndex: number; lastUpdated: number }> = {};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { projectId } = body;

    if (!projectId) {
      return NextResponse.json({ error: 'projectId is required' }, { status: 400 });
    }

    // Initialize project progress if not exists
    if (!projectProgress[projectId]) {
      projectProgress[projectId] = { currentIndex: -1, lastUpdated: Date.now() };
    }

    const progress = projectProgress[projectId];

    // Simulate progress every 5 seconds (advance to next stage)
    const timeSinceLastUpdate = Date.now() - progress.lastUpdated;
    if (timeSinceLastUpdate > 3000) {
      if (progress.currentIndex < mockResponses.length - 1) {
        progress.currentIndex++;
      }
      progress.lastUpdated = Date.now();
    }

    // Ensure we always return a valid response
    const safeIndex = Math.max(progress.currentIndex, 0);
    const response = mockResponses[safeIndex];

    console.log(` Status for ${projectId}:`, response);

    return NextResponse.json(response);
  } catch (error) {
    console.error(' Error in /status:', error);
    return NextResponse.json({ error: 'Failed to fetch status' }, { status: 500 });
  }
}
