import * as Tooltip from '@radix-ui/react-tooltip'
import { Mail, Phone, Send, MessageCircle, type LucideIcon } from 'lucide-react'
import type { Stage } from '@/shared/api/types'
import { StatusBadge } from './StatusBadge'
import { cn } from './cn'

export type CardChannel = 'email' | 'telegram' | 'phone' | 'whatsapp'

export interface CandidateCardProps {
  name: string
  role?: string
  avatarUrl?: string
  status?: Stage
  matchScore?: number
  channels?: CardChannel[]
  onClick?: () => void
  className?: string
}

const CHANNEL_ICON: Record<CardChannel, LucideIcon> = {
  email: Mail,
  telegram: Send,
  phone: Phone,
  whatsapp: MessageCircle,
}

function initials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('')
}

function MatchRing({ score, size }: { score: number; size: number }) {
  const stroke = 3
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - Math.max(0, Math.min(100, score)) / 100)
  const center = size / 2
  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      className="absolute inset-0 -rotate-90"
    >
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke="var(--surface-sunken)"
        strokeWidth={stroke}
      />
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke="var(--accent-blue)"
        strokeWidth={stroke}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
      />
    </svg>
  )
}

/**
 * Opaque candidate card (content layer): 44px avatar with an optional match
 * ring, name (Headline), role (Subhead), a StatusBadge and channel icons.
 */
export function CandidateCard({
  name,
  role,
  avatarUrl,
  status,
  matchScore,
  channels,
  onClick,
  className,
}: CandidateCardProps) {
  const avatarSize = 44
  const hasMatch = typeof matchScore === 'number'

  const avatar = (
    <div
      className="relative shrink-0 overflow-hidden rounded-pill bg-[var(--surface-sunken)]"
      style={{ width: avatarSize, height: avatarSize }}
    >
      {avatarUrl ? (
        <img
          src={avatarUrl}
          alt={name}
          className="h-full w-full object-cover"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center text-sm font-semibold text-[var(--text-secondary)]">
          {initials(name)}
        </div>
      )}
      {hasMatch && <MatchRing score={matchScore as number} size={avatarSize} />}
    </div>
  )

  return (
    <div
      className={cn(
        'flex items-center gap-3 rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] p-3 shadow-card',
        onClick != null && 'cursor-pointer',
        className,
      )}
      onClick={onClick}
    >
      <Tooltip.Provider delayDuration={200}>
        {hasMatch ? (
          <Tooltip.Root>
            <Tooltip.Trigger asChild>
              <span className="relative inline-block">{avatar}</span>
            </Tooltip.Trigger>
            <Tooltip.Portal>
              <Tooltip.Content
                side="top"
                className="glass glass--regular rounded-sm px-2 py-1 text-xs"
              >
                Совпадение {matchScore}%
                <Tooltip.Arrow className="fill-[var(--glass-bg-identity)]" />
              </Tooltip.Content>
            </Tooltip.Portal>
          </Tooltip.Root>
        ) : (
          avatar
        )}
      </Tooltip.Provider>

      <div className="min-w-0 flex-1">
        <div className="truncate text-base font-semibold text-[var(--text-primary)]">
          {name}
        </div>
        {role != null && (
          <div className="truncate text-sm text-[var(--text-secondary)]">
            {role}
          </div>
        )}
      </div>

      {status != null && <StatusBadge stage={status} />}

      {channels != null && channels.length > 0 && (
        <div className="flex shrink-0 items-center gap-1 text-[var(--text-tertiary)]">
          {channels.map((channel) => {
            const Icon = CHANNEL_ICON[channel]
            return <Icon key={channel} size={16} />
          })}
        </div>
      )}
    </div>
  )
}
