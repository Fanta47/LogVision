import Image from "next/image";
export function VermegLogo({ small = false }: { small?: boolean }) {
  return <div className="flex items-center gap-2">
    <Image src={small ? "/assets/vermeg-slash-clean.png" : "/assets/vermeg-logo-brand.png"} alt="Vermeg" width={small ? 26 : 180} height={small ? 26 : 54} className="h-auto w-auto" />
  </div>;
}
