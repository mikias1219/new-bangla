"use client";

import { useState } from "react";
import { Twitter, Facebook, Instagram, Linkedin, Share2 } from "lucide-react";

interface SocialMediaIntegrationProps {
  message: string;
  onShare?: (platform: string, message: string) => void;
}

export default function SocialMediaIntegration({ message, onShare }: SocialMediaIntegrationProps) {
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [isSharing, setIsSharing] = useState(false);

  const platforms = [
    { id: 'twitter', name: 'Twitter', icon: Twitter, color: 'bg-blue-400' },
    { id: 'facebook', name: 'Facebook', icon: Facebook, color: 'bg-blue-600' },
    { id: 'instagram', name: 'Instagram', icon: Instagram, color: 'bg-pink-500' },
    { id: 'linkedin', name: 'LinkedIn', icon: Linkedin, color: 'bg-blue-700' },
  ];

  const handlePlatformToggle = (platformId: string) => {
    setSelectedPlatforms(prev =>
      prev.includes(platformId)
        ? prev.filter(p => p !== platformId)
        : [...prev, platformId]
    );
  };

  const handleShare = async () => {
    if (selectedPlatforms.length === 0 || !message.trim()) return;

    setIsSharing(true);
    try {
      for (const platform of selectedPlatforms) {
        if (onShare) {
          await onShare(platform, message);
        } else {
          // Fallback: open share URLs
          await shareToPlatform(platform, message);
        }
      }

      alert(`Message shared to ${selectedPlatforms.join(', ')} successfully!`);
      setSelectedPlatforms([]);
    } catch (error) {
      console.error('Sharing failed:', error);
      alert('Failed to share message. Please try again.');
    } finally {
      setIsSharing(false);
    }
  };

  const shareToPlatform = async (platform: string, message: string) => {
    const encodedMessage = encodeURIComponent(message);
    const currentUrl = encodeURIComponent(window.location.href);

    let shareUrl = '';

    switch (platform) {
      case 'twitter':
        shareUrl = `https://twitter.com/intent/tweet?text=${encodedMessage}&url=${currentUrl}`;
        break;
      case 'facebook':
        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${currentUrl}&quote=${encodedMessage}`;
        break;
      case 'linkedin':
        shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${currentUrl}&title=${encodedMessage}`;
        break;
      case 'instagram':
        // Instagram doesn't support direct sharing via URL, so we'll copy to clipboard
        await navigator.clipboard.writeText(message);
        alert('Message copied to clipboard. Please paste it manually in Instagram.');
        return;
      default:
        return;
    }

    if (shareUrl) {
      window.open(shareUrl, '_blank', 'width=600,height=400');
    }
  };

  if (!message.trim()) {
    return null;
  }

  return (
    <div className="border-t border-gray-200 p-4 bg-gray-50">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Share2 className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">Share AI Response</span>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-3">
        {platforms.map((platform) => {
          const Icon = platform.icon;
          const isSelected = selectedPlatforms.includes(platform.id);

          return (
            <button
              key={platform.id}
              onClick={() => handlePlatformToggle(platform.id)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-white text-sm font-medium transition-colors ${
                isSelected
                  ? `${platform.color} ring-2 ring-offset-2 ring-gray-300`
                  : 'bg-gray-400 hover:bg-gray-500'
              }`}
            >
              <Icon className="w-4 h-4" />
              {platform.name}
            </button>
          );
        })}
      </div>

      <div className="flex justify-between items-center">
        <div className="text-xs text-gray-500">
          {selectedPlatforms.length > 0
            ? `Share to ${selectedPlatforms.length} platform${selectedPlatforms.length > 1 ? 's' : ''}`
            : 'Select platforms to share'
          }
        </div>

        <button
          onClick={handleShare}
          disabled={selectedPlatforms.length === 0 || isSharing}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSharing ? 'Sharing...' : 'Share'}
        </button>
      </div>
    </div>
  );
}

// Helper function to integrate with AI responses
export const createShareableContent = (aiResponse: string, context?: string) => {
  const maxLength = 280; // Twitter limit
  let content = aiResponse;

  if (context) {
    content = `${context}\n\n${aiResponse}`;
  }

  // Truncate if too long
  if (content.length > maxLength) {
    content = content.substring(0, maxLength - 3) + '...';
  }

  return content;
};
