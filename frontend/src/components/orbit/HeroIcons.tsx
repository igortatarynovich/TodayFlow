"use client";

export function SelfDiscoveryIcon() {
  return (
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Профиль головы */}
      <path
        d="M16 8C12.686 8 10 10.686 10 14C10 17.314 12.686 20 16 20C19.314 20 22 17.314 22 14C22 10.686 19.314 8 16 8Z"
        stroke="#D4AF37"
        strokeWidth="1.5"
        fill="none"
      />
      {/* Линия/спираль внутри головы - самопознание */}
      <path
        d="M12 14C12 16 13 18 16 18C19 18 20 16 20 14"
        stroke="#D4AF37"
        strokeWidth="1.2"
        fill="none"
        strokeLinecap="round"
      />
      {/* Спираль мысли */}
      <path
        d="M16 12C15 11 14 11.5 14 12.5C14 13.5 15 14 16 14C17 14 18 13.5 18 12.5C18 11.5 17 11 16 12Z"
        stroke="#D4AF37"
        strokeWidth="1"
        fill="none"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function CardOfDayIcon() {
  return (
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Первая карта (задняя) */}
      <rect
        x="6"
        y="8"
        width="12"
        height="18"
        rx="2"
        stroke="#D4AF37"
        strokeWidth="1.5"
        fill="none"
        opacity="0.7"
        transform="rotate(-5 12 17)"
      />
      {/* Вторая карта (передняя) */}
      <rect
        x="14"
        y="6"
        width="12"
        height="18"
        rx="2"
        stroke="#D4AF37"
        strokeWidth="1.5"
        fill="none"
      />
      {/* Солнечный знак на передней карте */}
      <circle
        cx="20"
        cy="15"
        r="4"
        stroke="#D4AF37"
        strokeWidth="1.2"
        fill="none"
      />
      {/* Лучи солнца */}
      <path
        d="M20 11L20 9M20 21L20 23M11 15L9 15M23 15L25 15M12.5 12.5L11 11M27.5 17.5L29 19M12.5 17.5L11 19M27.5 12.5L29 11"
        stroke="#D4AF37"
        strokeWidth="1"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function PracticesIcon() {
  return (
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Медитирующая фигура */}
      <ellipse
        cx="16"
        cy="20"
        rx="6"
        ry="4"
        stroke="#D4AF37"
        strokeWidth="1.5"
        fill="none"
      />
      {/* Голова */}
      <circle
        cx="16"
        cy="12"
        r="3"
        stroke="#D4AF37"
        strokeWidth="1.5"
        fill="none"
      />
      {/* Руки в медитативной позе */}
      <ellipse
        cx="16"
        cy="18"
        rx="4"
        ry="2"
        stroke="#D4AF37"
        strokeWidth="1.2"
        fill="none"
      />
      {/* Лотос над головой */}
      <path
        d="M16 9L14 7L16 5L18 7L16 9Z"
        stroke="#D4AF37"
        strokeWidth="1.2"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Лепестки лотоса */}
      <path
        d="M16 5L15 4L16 3L17 4M14 7L13 6L14 5L15 6M18 7L19 6L18 5L17 6"
        stroke="#D4AF37"
        strokeWidth="1"
        fill="none"
        strokeLinecap="round"
      />
      {/* Лучи света */}
      <path
        d="M16 2L16 0M10 9L8 8M22 9L24 8M8 15L6 14M24 15L26 14"
        stroke="#D4AF37"
        strokeWidth="0.8"
        strokeLinecap="round"
        opacity="0.6"
      />
    </svg>
  );
}

