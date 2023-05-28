/* app/api/llm.ts */

import { createLLMService } from "usellm";

export const runtime = "edge";

const llmService = createLLMService({
  openaiApiKey: process.env.OPENAI_API_KEY,
  actions: [
    "chat",
  "transcribe",
  "embed",
  "speak",
  "generateImage",
  "editImage",
  "imageVariation"
  ],

});

llmService.registerTemplate({
    id: "story-generator",
    max_tokens: 2048,
    model: "gpt-3.5-turbo",
    temperature: 1,
  });

export async function POST(request: Request) {
  const body = await request.json();
  try {
    const { result } = await llmService.handle({ body, request });
    return new Response(result, { status: 200 });
  } catch (error: any) {
    return new Response(error.message, { status: error?.status || 400 });
  }
}
