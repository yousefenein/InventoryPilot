import type { IconSvgProps } from "./types";

import React from "react";

export const CsfIcon: React.FC<IconSvgProps> = ({ size = 32, width, height, ...props }) => (
  <svg
    fill="none"
    height={size || height}
    viewBox="0 0 160 160"
    width={size || width}
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <defs>
      <clipPath id="circleClip">
        <circle cx="80" cy="80" r="80" />
      </clipPath>
    </defs>
    <g clipPath="url(#circleClip)">
      <rect width="160" height="160" fill="#FF0000" />
      <path d="M80 0 L160 80 L80 160 Z" fill="#8B0000" />
      <text
        x="30"
        y="85"
        fill="#FFFFFF"
        fontFamily="Arial, sans-serif"
        fontSize="30"
        fontWeight="bold"
      >
        CSF
      </text>
      <text
        x="30"
        y="125"
        fill="#FFFFFF"
        fontFamily="Arial, sans-serif"
        fontSize="11"
        letterSpacing="2"
      >
        INTERNATIONAL
      </text>
    </g>
  </svg>
);
