/* eslint-disable @next/next/no-img-element */
/** Creator photo inside an Instagram-style story ring. Falls back to the first letter of the handle. */
export function Avatar({ src, name, size = 56 }: { src?: string | null; name: string; size?: number }) {
  const letter = name.replace(/[^a-z0-9]/gi, "").charAt(0).toUpperCase() || "?";
  return (
    <span className="story-ring inline-block shrink-0" style={{ width: size, height: size }}>
      {src ? (
        <img src={src} alt="" width={size} height={size} loading="lazy" className="block size-full object-cover" />
      ) : (
        <span
          className="flex size-full items-center justify-center bg-surface-2 font-bold text-muted"
          style={{ fontSize: size * 0.38 }}
          aria-hidden
        >
          {letter}
        </span>
      )}
    </span>
  );
}
