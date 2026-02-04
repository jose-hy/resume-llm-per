<script lang="ts">
  import { createCombobox } from "svelte-headlessui";
  import Transition from "svelte-transition";
  import CloseIcon from "$lib/icons/close_icon.svelte";
  import CaretDownIcon from "$lib/icons/caret_down_icon.svelte";

  const {
    data,
    setData,
    selected,
    setSelected,
    editing = false,
  }: { data: string[]; setData: (data: string[]) => void; selected?: string[]; setSelected?: (selected: string[]) => void; editing?: boolean } = $props();

  const combobox = createCombobox({
    label: "",
    selected: selected ?? [],
  });

  const filtered = $derived(
    data.filter((item) => {
      return item
        .toLowerCase()
        .replace(/\s+/g, "")
        .includes($combobox.filter.toLowerCase().replace(/\s+/g, ""));
    })
  );

  function onSelect() {
    try {
      setSelected?.($combobox.selected);
    } catch (e) {
      console.error("setSelected not provided", e);
    }
  }

  function onChange(e: Event) {
    setData((e as CustomEvent).detail.selected);
    try {onSelect();} catch (e) {};
  }
</script>

<div>
  <div class="relative mt-1">
    <span class="inline-block w-full rounded-md">
      <button
        use:combobox.button
        onchange={onChange}
        class="focus:shadow-outline-teal relative w-full cursor-default rounded-md [border:1px_solid_#DADADA] bg-white py-2 pl-2 pr-10 text-left text-sm transition duration-150 ease-in-out focus:border-teal-300 focus:outline-none sm:leading-5"
      >
        <div class="flex flex-wrap gap-2">
          {#if !editing}
          {#each $combobox.selected as selected (selected)}
            <span
              class="flex items-center gap-1 rounded bg-blue-50 px-2 py-0.5"
            >
              <span>{selected}</span>
              <div use:combobox.deselect={selected}><CloseIcon /></div>
            </span>
          {/each}
          {/if}
          <input
            use:combobox.input
            onchange={onChange}
            placeholder="Search&hellip;"
            class="w-auto border-none py-1 text-sm leading-5 text-gray-900 focus:outline-none"
          />
        </div>
        <span
          class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2"
        >
          <CaretDownIcon />
        </span>
      </button>
    </span>

    <Transition
      show={$combobox.expanded}
      leave="transition ease-in duration-100"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
    >
      <ul
        use:combobox.items
        class="z-10 absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-sm shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
        class:absolute={!editing}
      >
        {#each filtered as value}
          {@const active = $combobox.active === value}
          {@const selected = $combobox.selected.includes(value)}
          <li
            class="relative cursor-default select-none py-2 pl-4 pr-9 focus:outline-none {active
              ? 'bg-gray-100 text-white'
              : 'text-gray-900'}"
            use:combobox.item={{ value }}
          >
            <span
              class="block truncate {selected
                ? 'font-semibold'
                : 'font-normal'}">{value}</span
            >
            {#if selected}
              <span
                class="absolute inset-y-0 right-0 flex items-center pr-3 {active
                  ? 'text-white'
                  : '#CEE6F1'}"
              >
              </span>
            {/if}
          </li>
        {:else}
          <li
            class="relative cursor-default select-none py-2 pl-10 pr-4 text-gray-900"
          >
            <span class="block truncate font-normal">Nothing found</span>
          </li>
        {/each}
      </ul>
    </Transition>
    {#if editing}
    <div class="flex mt-8px gap-12px flex-row flex-wrap">
      {#each $combobox.selected as selected (selected)}
        <span
          class="rounded-6px [border:2px_solid_#000000] resize-none p-4px flex items-center"
        >
          <span>{selected}</span>
          <div use:combobox.deselect={selected}><CloseIcon /></div>
        </span>
      {/each}
      </div>
    {/if}
  </div>
</div>
