import type { APIRoute } from 'astro';
import { RESEND_API_KEY, RESEND_SENDER_EMAIL, CONTACT_EMAIL_RECIPIENT } from 'astro:env/server';

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json();
    const { name, email, message } = body;

    // Validation
    if (!name || !email || !message) {
      return new Response(JSON.stringify({ error: "Name, email, and message are required." }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    // Secrets set in Cloudflare Pages dashboard, read via Astro v6 env module
    const resendApiKey = RESEND_API_KEY;
    const recipientEmail = CONTACT_EMAIL_RECIPIENT ?? "globalaerosols@gmail.com";
    const senderEmail = RESEND_SENDER_EMAIL ?? "inquiry@globalaerosols.com";

    if (!resendApiKey) {
      console.error("[Resend API Error]: RESEND_API_KEY is not defined in the environment.");
      return new Response(JSON.stringify({ error: "The contact form service is currently offline. Please email us directly." }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }

    // Format email contents
    const subject = `New Collaboration Inquiry from ${name}`;
    const textContent = `Name: ${name}\nEmail: ${email}\n\nCollaboration Inquiry Details:\n${message}`;
    const htmlContent = `
      <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; background-color: #ffffff; color: #1e293b;">
        <h2 style="font-size: 1.5rem; font-weight: 700; color: #0f172a; border-bottom: 2px solid #0968e5; padding-bottom: 12px; margin-top: 0;">New Synthesis Inquiry</h2>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
          <tr>
            <td style="padding: 6px 0; font-weight: 600; color: #64748b; width: 120px;">Name:</td>
            <td style="padding: 6px 0; color: #0f172a;">${name}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; font-weight: 600; color: #64748b;">Email:</td>
            <td style="padding: 6px 0; color: #0968e5;"><a href="mailto:${email}" style="color: #0968e5; text-decoration: none;">${email}</a></td>
          </tr>
        </table>
        <div style="margin-top: 24px;">
          <h4 style="margin: 0 0 8px 0; font-size: 0.95rem; font-weight: 600; color: #64748b;">Collaboration Message:</h4>
          <div style="padding: 16px; border-left: 4px solid #0968e5; background-color: #f8fafc; font-size: 1rem; line-height: 1.6; white-space: pre-wrap; color: #334155; border-radius: 0 8px 8px 0;">${message}</div>
        </div>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0 15px 0;" />
        <p style="font-size: 0.8rem; color: #94a3b8; text-align: center; margin: 0;">Submitted via www.globalaerosols.com contact portal.</p>
      </div>
    `;

    // Send email using Resend API via fetch
    const response = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${resendApiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        from: `Global Aerosols <${senderEmail}>`,
        to: recipientEmail,
        reply_to: email,
        subject: subject,
        text: textContent,
        html: htmlContent
      })
    });

    const data = await response.json() as any;

    if (!response.ok) {
      console.error("[Resend Delivery Error]:", data);
      return new Response(JSON.stringify({ error: data.message || "Failed to deliver email through Resend." }), {
        status: response.status,
        headers: { "Content-Type": "application/json" }
      });
    }

    return new Response(JSON.stringify({ success: true, id: data.id }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });

  } catch (err: any) {
    console.error("[Contact API server error]:", err);
    return new Response(JSON.stringify({ error: "Internal server error occurred." }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
};
