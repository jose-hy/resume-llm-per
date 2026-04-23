<!--
This is all derivative of the codepen and gist linked below. I claim none of it except the structure of the component.
Any work in here that is original enough to need a license is offered under the MIT license:
https://github.com/IQAndreas/markdown-licenses/blob/master/mit.md
-->
<script lang="ts">
    import { boolean, number, string } from "valibot";

    let { userFullName = "User Name",
    width = 32,
    round = true,
    src = "",
    avatarImage, }: {
        userFullName: string;
        width: number;
        round: boolean;
        src?: string;
        avatarImage?: HTMLImageElement;
    } = $props();

    /*
     * LetterAvatar
     *
     * Artur Heinze
     * Create Letter avatar based on Initials
     * based on https://gist.github.com/leecrossley/6027780
     * 
     * This component is based on https://codepen.io/arturheinze/pen/ZGvOMw
     */
    function LetterAvatar(name: String, size: number) {
        name = name || "";
        size = size || 60;

        var nameSplit = String(name).toUpperCase().split(" "),
            initials,
            charIndex,
            canvas,
            context,
            dataURI;

        if (nameSplit.length == 1) {
            initials = nameSplit[0] ? nameSplit[0].charAt(0) : "?";
        } else {
            initials = nameSplit[0].charAt(0) + nameSplit[1].charAt(0);
        }

        if (window.devicePixelRatio) {
            size = size * window.devicePixelRatio;
        }

        charIndex = (initials == "?" ? 72 : initials.charCodeAt(0)) - 64;
        canvas = document.createElement("canvas");
        canvas.width = size;
        canvas.height = size;
        context = canvas.getContext("2d");
        context.fillStyle = "#DDDDDD";
        context?.fillRect(0, 0, canvas.width, canvas.height);
        context.font = Math.round(canvas.width / 2) + "px Arial";
        context.textAlign = "center";
        context.fillStyle = "#000000";
        context?.fillText(initials, size / 2, size / 1.5);

        dataURI = canvas.toDataURL();
        canvas = null;

        return dataURI;
    }

    $effect(() => {
        try {
        avatarImage.src = src !== "" ? src : LetterAvatar(userFullName, width); }
        catch (e) {};
    });
</script>

<style>
    .round {
        border-radius: 50%;
    }
    img {
        border-radius: 4px;
    }
</style>

<img
    bind:this={avatarImage}
    class:round={round}
    {width}
    height={width}
    alt={userFullName} />