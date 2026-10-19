<script lang="ts">
  import { createDialog } from "svelte-headlessui";
  import Transition from "svelte-transition";
  import { supabase } from "./supabaseClient.js";
  import CloseIcon from "$lib/icons/close_icon.svelte";
  import Spacer from "./spacer.svelte";
  import { onMount } from "svelte";

  const {
    description,
    title,
    company,
    city,
    abbrState,
    apply_link,
    formattedTime,
    userID,
    sessionID,
    applied,
  } = $props();
  const dialog = createDialog();
  let page = $state("overview");
  let apply = $state(applied ? "View Application" : "Apply");

  const handleLearn = async () => {
    dialog.open();
    const statusError = await supabase.from("analytics").upsert({
      user_id: userID,
      type: "jobs_viewed",
      data: {
        session_id: sessionID,
        viewed: 1,
        title,
        company,
        apply_link,
        state: abbrState,
      }
    });
    console.log("any error: ", statusError);
  }

</script>

<button
  type="button"
  class="[border:1px_solid_black] rounded-4px px-12px py-4px"
  onclick={handleLearn}>Learn more</button
>

<div class="relative z-10">
  <Transition show={$dialog.expanded}>
    <Transition
      enter="ease-out duration-300"
      enterFrom="opacity-0"
      enterTo="opacity-100"
      leave="ease-in duration-200"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
    >
      <button
        class="fixed inset-0 bg-black bg-opacity-25"
        onclick={dialog.close}>close</button
      >
    </Transition>

    <div class="fixed inset-0 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4 text-center">
        <Transition
          enterFrom="opacity-0 scale-95"
          enter="ease-out duration-300"
          enterTo="opacity-100 scale-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100 scale-100"
          leaveTo="opacity-0 scale-95"
        >
          <div
            class="w-full max-w-[800px] transform overflow-hidden rounded-12px
              bg-white p-6 text-left align-middle shadow-xl transition-all"
            use:dialog.modal
          >
            <div class="flex justify-between gap-12px">
              <div>
                <p class="font-600 text-24px">{title}</p>
                <p>
                  {company} | {city}, {abbrState} | {formattedTime}
                </p>
              </div>
              <div class="flex gap-12px justify-end">
                <a
                  class="bg-black text-white rounded-4px px-12px py-4px h-[32px]"
                  href={apply_link}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {#if applied}
                    Go
                  {:else}
                    Apply
                  {/if}
                </a>
                <button onclick={dialog.close} class="cursor-pointer w-[32px] h-[32px]">
                  <CloseIcon/>
                </button>
              </div>
            </div>
            <Spacer axis="y" size="24" />
            <div
              class="flex gap-16px bg-white px-12px py-8px
              [border:1px_solid_#D9D9D9] rounded-7px w-min"
            >
              <button
                onclick={() => (page = "overview")}
                class={page === "overview"
                  ? "[border:1px_solid_#E6E6E6] bg-[#F7F7F7] px-8px py-4px rounded-6px"
                  : ""}>Overview</button>
            </div>
            <Spacer size={24} axis="y" />
            {#if page === "overview"}
              <p class="whitespace-pre-line">{description}</p>
            {/if}
            <Spacer size={24} axis="y" />
            <a
              class="bg-black text-white rounded-4px px-12px py-4px h-full"
              href={apply_link}
              target="_blank"
              rel="noopener noreferrer"
            >
              {apply}
            </a>
            <button
              type="button"
              class="[border:1px_solid_black] rounded-4px px-12px py-4px"
              onclick={dialog.close}
            >
              Back
            </button>
          </div>
        </Transition>
      </div>
    </div>
  </Transition>
</div>
