import api from "../api/axios";

export async function previewSanitization(prompt) {

    const response = await api.post(
        "/ai/preview-sanitization",
        {
            prompt
        }
    );

    return response.data;
}

export async function generateResponse(
    prompt,
    task
) {

    const response = await api.post(
        "/ai/generate",
        {
            prompt,
            task
        }
    );

    return response.data;
}