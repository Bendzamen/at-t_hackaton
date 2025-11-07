import { NextRequest, NextResponse } from 'next/server';

interface StatusEntry {
  stage: string;
  message: string;
  index: number;
  zip?: string;
}

export type StatusBlock = string | StatusEntry[];

// Mock data for the project (simulate incremental stages)
const data: StatusBlock[] = [
  'Initial PDF Submission',
  [{ stage: 'Analyzing', message: 'Analyzing your request...', index: 0 }],
  'Initial PDF Submission',
  [
    { stage: 'Analyzing', message: 'Analyzing your request...', index: 0 },
    { stage: 'Processing', message: 'Processing files and generating output...', index: 1 },
  ],
  'Initial PDF Submission',
  [
    { stage: 'Analyzing', message: 'Analyzing your request...', index: 0 },
    { stage: 'Processing', message: 'Processing files and generating output...', index: 1 },
    { stage: 'Finalizing', message: 'Finalizing the project structure...', index: 2 },
  ],
  'Initial PDF Submission',
  [
    { stage: 'Analyzing', message: 'Analyzing your request...', index: 0 },
    { stage: 'Processing', message: 'Processing files and generating output...', index: 1 },
    { stage: 'Finalizing', message: 'Finalizing the project structure...', index: 2 },
    {
      stage: 'Complete',
      message: '✅ Your project is ready!',
      index: 3,
      zip: 'data:application/zip;base64,UEsDBBQACAAIAH...',
    },
  ],
  'Can you make it better?',
  [
    { stage: 'Analyzing', message: 'Analyzing your request...', index: 0 },
    { stage: 'Processing', message: 'Processing files and generating output...', index: 1 },
    { stage: 'Finalizing', message: 'Finalizing the project structure...', index: 2 },
    {
      stage: 'Complete',
      message: '✅ Your project is ready!',
      index: 3,
      zip: 'data:application/zip;base64,UEsDBBQACAAIAH...',
    },
  ],
];

// Global state to simulate incremental progress
let currentIndex = -1;
let lastUpdated = Date.now();

export async function POST(request: NextRequest) {
  try {
    const now = Date.now();
    const timeSinceLastUpdate = now - lastUpdated;

    // Increment index every 3 seconds to simulate progress
    if (timeSinceLastUpdate > 3000 && currentIndex < data.length - 1) {
      currentIndex++;
      lastUpdated = now;
    }

    // Slice the data up to the current index to simulate partial progress
    const response = data.slice(0, currentIndex + 1);

    console.log('Simulated status slice:', response);

    return NextResponse.json({ data: response });
  } catch (error) {
    console.error('Error in /status:', error);
    return NextResponse.json({ error: 'Failed to fetch status' }, { status: 500 });
  }
}
