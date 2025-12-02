"use client";

import Link from "next/link";

export default function ModuleCard({ icon: Icon, title, description, href }) {
  return (
    <div className="bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 p-6 flex flex-col h-full">
      {/* Icon */}
      <div className="mb-4 flex items-center justify-center w-14 h-14 rounded-lg bg-white shadow-sm">
        <Icon className="w-8 h-8 text-purple-600" />
      </div>

      {/* Title */}
      <h3 className="text-xl font-semibold text-gray-800 mb-2">{title}</h3>

      {/* Description */}
      <p className="text-gray-600 text-sm flex-grow mb-6">{description}</p>

      {/* Button */}
      <Link
        href={href}
        className="inline-flex items-center justify-center px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200 transform hover:scale-105"
      >
        Open Tool
      </Link>
    </div>
  );
}
