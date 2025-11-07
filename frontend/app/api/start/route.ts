import { type NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    // For now, just validate and return the file name
    const fileName = `${Date.now()}-${file.name}`;

    // In production, you would:
    // 1. Store the file using Vercel Blob, S3, or your storage service
    // 2. Process the file (convert DOCX to PDF on server-side if needed)
    // 3. Return a URL or reference to the stored file

    return NextResponse.json(
      {
        success: true,
        fileName: file.name,
        storedFileName: fileName,
        size: file.size,
        type: file.type,
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json({ error: 'Upload failed' }, { status: 500 });
  }
}
