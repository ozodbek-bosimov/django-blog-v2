document.addEventListener("DOMContentLoaded", function () {
  const ABOUT = window.ABOUT_CONFIG || {};
  const githubUrl = ABOUT.githubUrl || "";
  let ghUsername = null;
  if (githubUrl) {
    const match = githubUrl.match(/github\.com\/([a-zA-Z0-9_-]+)/);
    if (match && match[1]) ghUsername = match[1];
  }

  // Time-bucketed cache-buster: refreshes once per hour instead of every
  // page load. This lets the browser, Cloudflare and the upstream stat
  // services serve cached renders (less load, faster, fewer rate-limits)
  // while still keeping the data reasonably fresh.
  const cbStr = Math.floor(Date.now() / 3600000).toString();
  let statsUrl = "",
    langsUrl = "",
    streakUrl = "";

  // The Top-languages card needs a different intrinsic width per
  // breakpoint so it always looks balanced:
  //  • Desktop: it sits in a narrow side column, so a 320px card keeps
  //    its title/text the same visual size as the wider stats card.
  //  • Mobile: it spans the full width, so a wider 495px card fills the
  //    row with crisp, properly-sized text (no oversized title).
  const langsMq = window.matchMedia("(min-width: 640px)");
  const buildLangsUrl = (cardWidth) =>
    `https://github-readme-stats-salesp07.vercel.app/api/top-langs/?username=${ghUsername}&title_color=67e8f9&text_color=c9d1d9&icon_color=06b6d4&bg_color=00000000&hide_border=true&layout=compact&card_width=${cardWidth}&v=${cbStr}`;
  const currentLangsCardWidth = () => (langsMq.matches ? 320 : 495);

  if (ghUsername) {
    statsUrl = `https://github-readme-stats-salesp07.vercel.app/api?username=${ghUsername}&title_color=67e8f9&text_color=c9d1d9&icon_color=06b6d4&bg_color=00000000&hide_border=true&include_all_commits=true&count_private=true&rank_icon=github&show_icons=true&v=${cbStr}`;
    langsUrl = buildLangsUrl(currentLangsCardWidth());
    streakUrl = `https://github-readme-streak-stats-salesp07.vercel.app/?user=${ghUsername}&theme=dark&hide_border=true&background=00000000&stroke=334155&ring=06b6d4&fire=67e8f9&v=${cbStr}`;

    // Secretly preload early in the background
    setTimeout(() => {
      new Image().src = statsUrl;
      new Image().src = langsUrl;
      new Image().src = streakUrl;
    }, 50);
  }

  let leetcodePromise = null;
  const leetcodeUrl = ABOUT.leetcodeUrl || "";
  if (leetcodeUrl && leetcodeUrl.includes("leetcode.com")) {
    // The backend handles the fetching, caching, and CSS injection natively
    leetcodePromise = Promise.resolve(`/leetcode-proxy/?v=${cbStr}`);
  }

  const initGithubStats = function () {
    if (ghUsername) {
      const username = ghUsername;
      const statsImg = document.getElementById("github-stats-img");
      const langsImg = document.getElementById("github-langs-img");
      const streakImg = document.getElementById("github-streak-img");
      const container = document.getElementById("github-calendar-container");

      // Lock the contribution-calendar area to a FIXED height that is
      // computed the SAME way during loading, after load, and on
      // resize — so the card never resizes once the grid appears.
      // The reserve scales with the panel width and is kept a touch
      // taller than the grid's real rendered height, so the grid
      // always fits (no clipping) with at most a few px of slack.
      // 0.16 ≈ the grid's aspect ratio (7 day-rows over ~53 week-cols);
      // +14px roughly accounts for the date-range labels below it.
      const calWrap = document.getElementById("github-cal-wrap");
      const setCalReserve = () => {
        if (!calWrap) return;
        const w = calWrap.clientWidth;
        if (!w) return;
        calWrap.style.height = Math.round(0.16 * w + 14) + "px";
      };
      setCalReserve();
      window.addEventListener("resize", setCalReserve);

      // Best-effort sequential loading with per-item timeouts
      const items = [
        { id: "stats", el: statsImg, skel: "github-stats-skeleton" },
        { id: "langs", el: langsImg, skel: "github-langs-skeleton" },
        { id: "streak", el: streakImg, skel: "github-streak-skeleton" },
        { id: "cal", isCal: true },
      ];

      let calTurnReached = false;
      let calReadyToReveal = false;
      let revealCalendarFn = null;

      const tryRevealCal = () => {
        if (calTurnReached && calReadyToReveal && revealCalendarFn) {
          revealCalendarFn();
        }
      };

      const initCal = () => {
        calTurnReached = true;
        tryRevealCal();
      };

      const showImg = (img, skelId) => {
        if (!img) return;
        const skel = document.getElementById(skelId);
        if (skel) skel.style.display = "none";
        img.classList.replace("github-img-hidden", "github-img-show");
      };

      const startTurn = (index) => {
        if (index >= items.length) return;
        const item = items[index];
        item.isMyTurn = true;

        if (item.isCal) {
          initCal();
          return;
        }

        if (item.loaded) {
          showImg(item.el, item.skel);
          item.shown = true;
          setTimeout(() => startTurn(index + 1), 500);
        } else {
          item.timeout = setTimeout(() => {
            item.timedOut = true;
            startTurn(index + 1);
          }, 2000);
        }
      };

      const handleLoad = (index) => {
        const item = items[index];
        item.loaded = true;

        if (item.isMyTurn && !item.shown) {
          showImg(item.el, item.skel);
          item.shown = true;

          if (!item.timedOut) {
            clearTimeout(item.timeout);
            setTimeout(() => startTurn(index + 1), 500);
          }
        }
      };

      if (statsImg) {
        statsImg.onload = () => handleLoad(0);
        statsImg.src = statsUrl;
      } else items[0].loaded = true;

      if (langsImg) {
        langsImg.onload = () => handleLoad(1);
        langsImg.src = langsUrl;

        // Swap the languages card for the correctly-sized one
        // whenever we cross the mobile/desktop breakpoint.
        const swapLangs = () => {
          const next = buildLangsUrl(currentLangsCardWidth());
          if (langsImg.src !== next) langsImg.src = next;
        };
        if (langsMq.addEventListener) {
          langsMq.addEventListener("change", swapLangs);
        } else if (langsMq.addListener) {
          langsMq.addListener(swapLangs);
        }
      } else items[1].loaded = true;

      if (streakImg) {
        streakImg.onload = () => handleLoad(2);
        streakImg.src = streakUrl;
      } else items[2].loaded = true;

      const tryFallbackCalendar = () => {
        if (container) {
          container.innerHTML = `<img src="https://ghchart.rshah.org/06b6d4/${username}" alt="GitHub Contribution Calendar" style="width: 100%; height: auto; padding-bottom: 1rem; filter: invert(1) hue-rotate(180deg) brightness(1.2);" onerror="const p = this.closest('.profile-panel--full'); if(p) p.style.display='none';">`;
          container.style.opacity = "1";
          container.style.height = "auto";
          container.style.overflow = "visible";
          const skel = document.getElementById("github-cal-skeleton");
          if (skel) skel.style.display = "none";
        }
      };

      if (container && typeof GitHubCalendar !== "undefined") {
        revealCalendarFn = () => {
          if (container.dataset.revealed) return;
          container.dataset.revealed = "true";

          const skel = document.getElementById("github-cal-skeleton");
          if (skel) skel.style.display = "none";

          container.style.height = "auto";
          container.style.overflow = "visible";

          // Trigger the CSS animation to fade in the grid
          setTimeout(() => {
            container.style.opacity = "1";
            container.style.animation =
              "fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards";
          }, 100);

          // Hide the extra stats and footer link below the calendar
          const contribColumns = document.querySelectorAll(
            "#github-calendar-container .contrib-column",
          );
          contribColumns.forEach((el) => {
            if (
              el.parentElement &&
              el.parentElement.className.includes("flex-wrap")
            ) {
              el.parentElement.style.display = "none";
            }
            el.style.display = "none";
          });

          const textMuted = document.querySelectorAll(
            "#github-calendar-container .text-muted",
          );
          textMuted.forEach((el) => (el.style.display = "none"));
        };

        const enhanceCalendar = () => {
          const cells = document.querySelectorAll(
            "#github-calendar-container .ContributionCalendar-day",
          );
          const validCells = Array.from(cells).filter(
            (c) =>
              c.hasAttribute("data-date") &&
              c.getAttribute("data-level") !== null,
          );
          if (!validCells.length) return false;

          validCells.sort((a, b) =>
            a
              .getAttribute("data-date")
              .localeCompare(b.getAttribute("data-date")),
          );
          const lastCell = validCells[validCells.length - 1];

          lastCell.style.boxShadow =
            "0 0 0 1px #ffa116, inset 0 0 0 1px #ffa116";
          lastCell.style.boxSizing = "border-box";
          lastCell.style.backgroundColor = "transparent";

          const graphContainer = document.querySelector(
            "#github-calendar-container .calendar-graph",
          );
          if (
            graphContainer &&
            !graphContainer.querySelector(".calendar-range-labels")
          ) {
            const firstDate = validCells[0]
              .getAttribute("data-date")
              .replace(/-/g, ".");
            const lastDate = lastCell
              .getAttribute("data-date")
              .replace(/-/g, ".");

            const datesDiv = document.createElement("div");
            datesDiv.className = "calendar-range-labels";
            datesDiv.style.display = "flex";
            datesDiv.style.justifyContent = "space-between";
            datesDiv.style.fontSize = "0.75rem";
            datesDiv.style.color = "#f8fafc";
            datesDiv.style.marginTop = "0.4rem";
            datesDiv.style.fontFamily = "monospace, sans-serif";

            const firstSpan = document.createElement("span");
            firstSpan.textContent = firstDate;
            const lastSpan = document.createElement("span");
            lastSpan.textContent = lastDate;

            datesDiv.appendChild(firstSpan);
            datesDiv.appendChild(lastSpan);
            graphContainer.appendChild(datesDiv);
          }
          calReadyToReveal = true;

          // Scale the GitHub grid to fill the panel width, mirroring
          // how the LeetCode SVG (width:100%) fits its card.
          //
          // We use `transform: scale()` (NOT `zoom`). `zoom` forces a
          // layout reflow in which every cell is re-snapped to whole
          // device pixels; the accumulated rounding error lands on the
          // trailing columns, making the last week or two visibly wider
          // ("distorted"). `transform: scale()` is a uniform vector
          // scale applied after layout, so every cell shrinks by the
          // exact same factor and all columns stay perfectly even.
          // We then collapse the left-over natural-size layout box with
          // negative margins so it leaves no overflow/scroll or gap.
          const fitGithubCalendar = () => {
            // The github-calendar library renders an <svg>, while a
            // raw GitHub HTML proxy renders a <table>. Support both so
            // the grid always scales to fill the panel width (like the
            // LeetCode heatmap) instead of sitting left-aligned with
            // empty space on the right.
            const grid =
              container.querySelector(".ContributionCalendar-grid") ||
              container.querySelector("svg.js-calendar-graph-svg") ||
              container.querySelector(".calendar-graph svg") ||
              container.querySelector("svg") ||
              container.querySelector("table");
            if (!grid) return;
            grid.style.zoom = "";
            grid.style.transform = "none";
            grid.style.transformOrigin = "top left";
            grid.style.margin = "0";
            // Use real rendered geometry rather than reading the width
            // of GitHub's intermediate wrappers (they add a border,
            // `tmp-mx-3` margins and `flex-items-end` alignment, so their
            // reported widths are unreliable and caused the grid to spill
            // off the right edge). With transform-origin at top-left the
            // grid scales out from wherever it currently sits, so the
            // space available is simply: container right edge minus the
            // grid's current left edge.
            const gridRect = grid.getBoundingClientRect();
            const contRect = container.getBoundingClientRect();
            const naturalW = gridRect.width;
            const naturalH = gridRect.height;
            const avail = contRect.right - gridRect.left;
            if (!naturalW || avail <= 0) return;
            const scale = avail / naturalW;
            grid.style.transform = `scale(${scale})`;
            // transform doesn't shrink the layout box, so reclaim the
            // leftover width (prevents horizontal scroll) and height
            // (prevents an empty gap under the grid).
            grid.style.marginRight = `-${naturalW - avail}px`;
            grid.style.marginBottom = `-${naturalH * (1 - scale)}px`;
          };

          // Fit synchronously FIRST, so the grid is already scaled to
          // the panel width before we reveal it. Otherwise the grid
          // would flash at its natural size and then resize on the next
          // frame, changing the card height right after it loads.
          fitGithubCalendar();
          tryRevealCal();

          // Run again on the next frames (after fonts/layout settle).
          requestAnimationFrame(() => {
            fitGithubCalendar();
            requestAnimationFrame(fitGithubCalendar);
          });

          if (!container.dataset.fitBound) {
            container.dataset.fitBound = "true";
            // Re-fit whenever the panel resizes.
            if ("ResizeObserver" in window) {
              const ro = new ResizeObserver(() => fitGithubCalendar());
              ro.observe(container);
            } else {
              let resizeTimer = null;
              window.addEventListener("resize", () => {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(fitGithubCalendar, 150);
              });
            }
            // The calendar library may re-render/replace the table
            // after we fit it, which would drop our scale transform.
            // Watch for DOM changes and re-apply.
            if ("MutationObserver" in window) {
              const mo = new MutationObserver(() => {
                requestAnimationFrame(fitGithubCalendar);
              });
              mo.observe(container, { childList: true, subtree: true });
            }
          }
          return true;
        };

        const waitForCalendar = (attempt = 0) => {
          if (enhanceCalendar()) return;
          if (attempt < 20) {
            setTimeout(() => waitForCalendar(attempt + 1), 150);
          } else {
            // We tried 20 times and enhanceCalendar STILL returned false.
            // This means the GitHub calendar DOM is incompatible or proxy returned an error HTML.
            // We MUST use the fallback.
            tryFallbackCalendar();
          }
        };

        const initResult = GitHubCalendar(
          "#github-calendar-container",
          username,
          {
            responsive: true,
            tooltips: true,
            proxy: function (username) {
              // Try the primary remote proxy first
              return fetch(`https://github-calendar.js.org/${username}`)
                .then((r) => {
                  if (!r.ok) throw new Error("Primary proxy failed");
                  return r.text();
                })
                .catch(() => {
                  // Fallback to our internal Django proxy
                  return fetch(`/github-contributions/`).then((r) => {
                    if (!r.ok) throw new Error("Internal proxy failed");
                    return r.text();
                  });
                });
            },
          },
        );

        if (initResult && typeof initResult.then === "function") {
          initResult
            .then(() => waitForCalendar())
            .catch((e) => {
              console.error("GitHub Calendar error:", e);
              tryFallbackCalendar();
            });
        } else {
          waitForCalendar();
        }
      } else if (container) {
        // Library completely failed to load -> Setup sequential fallback
        revealCalendarFn = () => {
          if (container.dataset.revealed) return;
          container.dataset.revealed = "true";
          tryFallbackCalendar();
        };
        calReadyToReveal = true;
      }
      startTurn(0);
    }
  };

  const ghContainer = document.querySelector(".profile-card--github");
  if (ghContainer && "IntersectionObserver" in window) {
    const ghObserver = new IntersectionObserver(
      (entries, obs) => {
        if (
          entries[0].isIntersecting ||
          entries[0].boundingClientRect.top < window.innerHeight
        ) {
          obs.disconnect();
          initGithubStats();
        }
      },
      { rootMargin: "50px", threshold: 0.1 },
    );
    ghObserver.observe(ghContainer);
  } else {
    initGithubStats();
  }

  const initLeetcodeStats = function () {
    if (!leetcodePromise) return;
    const lcWrapper = document.getElementById("leetcode-stats-wrapper");
    if (!lcWrapper) return;

    leetcodePromise.then((finalUrl) => {
      lcWrapper.innerHTML = `<img id="leetcode-stats-svg" class="profile-media__img github-img-hidden" alt="LeetCode Stats">`;
      const lcImg = document.getElementById("leetcode-stats-svg");
      lcImg.onload = () => {
        lcWrapper.classList.remove("skeleton-loader");
        lcImg.classList.replace("github-img-hidden", "github-img-show");
      };
      lcImg.src = finalUrl;
    });
  };

  const lcContainer = document.querySelector(".profile-card--leetcode");
  if (lcContainer && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries, obs) => {
        if (
          entries[0].isIntersecting ||
          entries[0].boundingClientRect.top < window.innerHeight
        ) {
          obs.disconnect();
          initLeetcodeStats();
        }
      },
      { rootMargin: "50px", threshold: 0.1 },
    );
    observer.observe(lcContainer);
  } else {
    initLeetcodeStats();
  }
});
