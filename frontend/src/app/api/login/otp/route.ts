import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function POST(request: Request) {
    try {
        const formData = await request.formData();
        const email = formData.get('email') as string;

        if (!email) {
            return NextResponse.json({ status: "error", message: "Email is required" }, { status: 400 });
        }

        const { error } = await supabase.auth.signInWithOtp({
            email,
            options: {
                shouldCreateUser: true
            }
        });

        if (error) {
            console.error("OTP Request Error", error);
            return NextResponse.json({ status: "error", message: error.message });
        }

        return NextResponse.json({ status: "success", message: "OTP sent successfully." });
    } catch (e: any) {
        console.error("OTP Request Error", e);
        return NextResponse.json({ status: "error", message: e.message || "Unknown error" });
    }
}
