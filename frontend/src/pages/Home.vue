<template>
  <main class="min-h-screen bg-stone-50 text-stone-950">
    <section class="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-4 sm:px-6 lg:px-8">
      <header class="flex flex-col gap-4 rounded-[2rem] bg-gradient-to-br from-[#24351f] via-[#415f39] to-[#9f7b4a] p-6 text-white shadow-xl shadow-stone-300/40 md:flex-row md:items-end md:justify-between md:p-8">
        <div class="max-w-3xl">
          <p class="text-xs font-bold uppercase tracking-[0.24em] text-white/70">Poloway</p>
          <h1 class="mt-3 text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl">Your stable, simplified.</h1>
          <p class="mt-4 max-w-2xl text-base leading-7 text-white/78">
            A horse-first command centre for today’s care, open actions, money checks, and upcoming polo.
          </p>
        </div>
        <div class="grid min-w-52 grid-cols-2 gap-3 rounded-3xl bg-white/12 p-3 backdrop-blur">
          <MetricTile label="Horses" :value="home.data?.summary?.horses || 0" dark />
          <MetricTile label="Available" :value="home.data?.summary?.available_horses || 0" dark />
        </div>
      </header>

      <div v-if="home.error" class="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        Could not load the Poloway app data.
      </div>

      <div v-if="home.loading" class="rounded-3xl border border-stone-200 bg-white p-8 text-stone-500 shadow-sm">
        Loading your stable…
      </div>

      <template v-else>
        <nav class="sticky top-0 z-10 -mx-4 flex gap-2 overflow-x-auto bg-stone-50/92 px-4 py-3 backdrop-blur sm:mx-0 sm:rounded-full sm:border sm:border-stone-200 sm:bg-white/80">
          <button
            v-for="section in sections"
            :key="section.key"
            :class="[
              'whitespace-nowrap rounded-full px-4 py-2 text-sm font-bold transition',
              activeSection === section.key ? 'bg-stone-950 text-white shadow-lg shadow-stone-300' : 'text-stone-600 hover:bg-stone-100',
            ]"
            @click="activeSection = section.key"
          >
            {{ section.label }}
          </button>
        </nav>

        <section v-if="activeSection === 'home'" class="grid gap-6 lg:grid-cols-[1.35fr_0.65fr]">
          <Panel title="Today" eyebrow="Schedule" action-label="Open calendar" @action="openRoute('/app/owner-task/view/calendar/default')">
            <div v-if="todayItems.length" class="grid gap-3">
              <button
                v-for="item in todayItems"
                :key="`${item.doctype}-${item.name}`"
                class="grid grid-cols-[4.5rem_1fr_auto] items-center gap-3 rounded-2xl border border-stone-200 bg-white p-3 text-left transition hover:-translate-y-0.5 hover:shadow-md"
                @click="openDoc(item.doctype, item.name)"
              >
                <span class="text-xs font-black text-amber-800">{{ time(item.starts_on) || 'Today' }}</span>
                <span class="min-w-0">
                  <strong class="block truncate text-sm text-stone-950">{{ item.title }}</strong>
                  <small class="block truncate text-stone-500">{{ item.type }}<template v-if="item.horse"> · {{ item.horse }}</template></small>
                </span>
                <Badge :label="item.doctype" theme="gray" />
              </button>
            </div>
            <EmptyState v-else text="No open work scheduled for today." />
          </Panel>

          <section class="grid gap-6">
            <Panel title="Quick actions" eyebrow="Start">
              <div class="grid grid-cols-2 gap-3">
                <button
                  v-for="action in quickActions"
                  :key="action.label"
                  class="min-h-24 rounded-3xl border border-stone-200 bg-white p-4 text-left text-sm font-black text-stone-900 transition hover:-translate-y-0.5 hover:shadow-md"
                  @click="openRoute(action.route)"
                >
                  {{ action.label }}
                </button>
              </div>
            </Panel>

            <Panel title="Stable pulse" eyebrow="Overview">
              <div class="grid grid-cols-2 gap-3">
                <MetricTile label="Today" :value="home.data?.summary?.today_tasks || 0" />
                <MetricTile label="Issues" :value="home.data?.summary?.open_issues || 0" tone="warning" />
                <MetricTile label="Next 14 days" :value="home.data?.summary?.owner_actions || 0" />
                <MetricTile label="Unposted" :value="home.data?.money?.unposted || 0" />
              </div>
            </Panel>
          </section>
        </section>

        <section v-if="activeSection === 'horses'" class="grid gap-6">
          <Panel title="Your horses" eyebrow="Stable" action-label="Add horse" @action="openRoute('/app/horse/new-horse')">
            <div v-if="horses.length" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <button
                v-for="horse in horses"
                :key="horse.name"
                class="rounded-[1.75rem] border border-stone-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
                @click="openDoc('Horse', horse.name)"
              >
                <span class="mb-4 grid h-16 w-16 place-items-center rounded-3xl bg-gradient-to-br from-[#263720] to-[#8aa07e] text-2xl font-black text-white">
                  {{ horse.display_name?.charAt(0) || 'H' }}
                </span>
                <strong class="block truncate text-lg">{{ horse.display_name }}</strong>
                <small class="block truncate text-stone-500">{{ horse.current_location || horse.stable_number || 'No location set' }}</small>
                <span class="mt-4 flex justify-between gap-3 text-xs font-bold text-emerald-700">
                  <span>{{ horse.playing_status || 'No status' }}</span>
                  <span>{{ horse.open_tasks || 0 }} tasks</span>
                </span>
              </button>
            </div>
            <EmptyState v-else text="No horses are available yet." />
          </Panel>
        </section>

        <section v-if="activeSection === 'care'" class="grid gap-6 lg:grid-cols-2">
          <Panel title="Care activity" eyebrow="Health and training">
            <div class="grid grid-cols-2 gap-3">
              <MetricTile label="Feeds this week" :value="home.data?.care?.feeding_7d || 0" />
              <MetricTile label="Training this week" :value="home.data?.care?.training_7d || 0" />
              <MetricTile label="Medical 30d" :value="home.data?.care?.medical_30d || 0" />
              <MetricTile label="Follow-ups due" :value="home.data?.care?.compliance_due || 0" tone="warning" />
            </div>
          </Panel>
          <Panel title="Care shortcuts" eyebrow="Records">
            <div class="grid grid-cols-2 gap-3">
              <ActionButton label="Log care entry" route="/app/horse-care-entry/new-horse-care-entry" />
              <ActionButton label="Medical records" route="/app/horse-medical-record" />
              <ActionButton label="Training records" route="/app/horse-training-record" />
              <ActionButton label="Groom board" route="/app/task/view/kanban/Whiteboard" />
            </div>
          </Panel>
        </section>

        <section v-if="activeSection === 'money'" class="grid gap-6 lg:grid-cols-2">
          <Panel title="This month" eyebrow="Money">
            <div class="grid gap-3">
              <MoneyRow label="Income" :value="home.data?.money?.income" tone="positive" />
              <MoneyRow label="Outflow" :value="home.data?.money?.outflow" tone="negative" />
              <MoneyRow label="Net" :value="home.data?.money?.net" />
            </div>
          </Panel>
          <Panel title="Review queue" eyebrow="Accounting" action-label="Review" @action="openRoute('/app/query-report/Unposted Transactions')">
            <p class="text-sm leading-6 text-stone-600">
              Keep the accounting workflow simple: upload receipts, review extracted transactions, then post once ready.
            </p>
            <div class="mt-5 rounded-3xl bg-stone-100 p-5">
              <span class="text-sm font-bold text-stone-500">Unposted transactions</span>
              <strong class="mt-1 block text-4xl font-black">{{ home.data?.money?.unposted || 0 }}</strong>
            </div>
          </Panel>
        </section>

        <section v-if="activeSection === 'matches'" class="grid gap-6">
          <Panel title="Upcoming polo" eyebrow="Matches" action-label="Add match" @action="openRoute('/app/match-day/new-match-day')">
            <div v-if="matches.length" class="grid gap-3">
              <button
                v-for="match in matches"
                :key="match.name"
                class="grid grid-cols-[7rem_1fr_auto] items-center gap-3 rounded-2xl border border-stone-200 bg-white p-3 text-left transition hover:-translate-y-0.5 hover:shadow-md"
                @click="openDoc('Match Day', match.name)"
              >
                <span class="text-xs font-black text-amber-800">{{ date(match.match_date) }}</span>
                <span class="min-w-0">
                  <strong class="block truncate text-sm text-stone-950">{{ match.event_name }}</strong>
                  <small class="block truncate text-stone-500">{{ match.venue || 'No venue set' }}</small>
                </span>
                <Badge :label="match.status" theme="gray" />
              </button>
            </div>
            <EmptyState v-else text="No upcoming matches recorded." />
          </Panel>
        </section>
      </template>
    </section>
  </main>
</template>

<script setup>
import { Badge, createResource } from 'frappe-ui'
import { computed, h, ref } from 'vue'

const sections = [
  { key: 'home', label: 'Home' },
  { key: 'horses', label: 'Horses' },
  { key: 'care', label: 'Care' },
  { key: 'money', label: 'Money' },
  { key: 'matches', label: 'Polo' },
]

const activeSection = ref('home')

const home = createResource({
  url: 'polomanagement.poloway_home.get_home_data',
  auto: true,
})

const todayItems = computed(() => home.data?.today || [])
const horses = computed(() => home.data?.horses || [])
const matches = computed(() => home.data?.matches?.upcoming || [])
const quickActions = computed(() => home.data?.quick_actions || [])

function openDoc(doctype, name) {
  window.location.href = `/app/${doctype.toLowerCase().replaceAll(' ', '-')}/${name}`
}

function openRoute(route) {
  if (Array.isArray(route)) {
    const [kind, doctype, name] = route
    if (kind === 'Form') {
      window.location.href = `/app/${doctype.toLowerCase().replaceAll(' ', '-')}/${name}`
      return
    }
  }
  window.location.href = route
}

function time(value) {
  if (!value) return ''
  const text = String(value)
  return text.includes(' ') ? text.split(' ')[1]?.slice(0, 5) : text.slice(0, 5)
}

function date(value) {
  return value ? String(value).slice(0, 10) : ''
}

function currency(value) {
  return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })
}

const Panel = (props, { slots, emit }) => h(
  'article',
  { class: 'rounded-[1.75rem] border border-stone-200 bg-white/92 p-5 shadow-sm shadow-stone-200/60 backdrop-blur sm:p-6' },
  [
    h('div', { class: 'mb-5 flex items-start justify-between gap-4' }, [
      h('div', {}, [
        props.eyebrow ? h('p', { class: 'mb-2 text-xs font-black uppercase tracking-[0.18em] text-emerald-700' }, props.eyebrow) : null,
        h('h2', { class: 'text-2xl font-black tracking-tight text-stone-950' }, props.title),
      ]),
      props.actionLabel ? h('button', { class: 'rounded-full bg-stone-950 px-4 py-2 text-sm font-bold text-white', onClick: () => emit('action') }, props.actionLabel) : null,
    ]),
    slots.default?.(),
  ],
)
Panel.props = ['title', 'eyebrow', 'actionLabel']
Panel.emits = ['action']

const MetricTile = (props) => h(
  'div',
  { class: [
    'rounded-3xl p-4',
    props.dark ? 'bg-white/12 text-white' : 'border border-stone-200 bg-stone-50 text-stone-950',
  ] },
  [
    h('strong', { class: ['block text-3xl font-black', props.tone === 'warning' ? 'text-amber-700' : ''] }, props.value),
    h('span', { class: ['text-xs font-bold', props.dark ? 'text-white/70' : 'text-stone-500'] }, props.label),
  ],
)
MetricTile.props = ['label', 'value', 'tone', 'dark']

const EmptyState = (props) => h('div', { class: 'rounded-3xl border border-dashed border-stone-200 bg-stone-50 p-6 text-sm text-stone-500' }, props.text)
EmptyState.props = ['text']

const ActionButton = (props) => h('button', {
  class: 'min-h-24 rounded-3xl border border-stone-200 bg-stone-50 p-4 text-left text-sm font-black text-stone-900 transition hover:-translate-y-0.5 hover:bg-white hover:shadow-md',
  onClick: () => openRoute(props.route),
}, props.label)
ActionButton.props = ['label', 'route']

const MoneyRow = (props) => h('div', { class: 'flex items-center justify-between rounded-3xl border border-stone-200 bg-stone-50 p-5' }, [
  h('span', { class: 'text-sm font-bold text-stone-500' }, props.label),
  h('strong', { class: ['text-2xl font-black', props.tone === 'positive' ? 'text-emerald-700' : props.tone === 'negative' ? 'text-red-700' : 'text-stone-950'] }, currency(props.value)),
])
MoneyRow.props = ['label', 'value', 'tone']
</script>
