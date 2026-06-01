import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LottoAI - วิเคราะห์หวยด้วย AI",
  description: "วิเคราะห์ข้อมูลหวยรัฐบาลไทยย้อนหลังครึ่งภาคด้วย AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="th">
      <body>{children}</body>
    </html>
  );
}
