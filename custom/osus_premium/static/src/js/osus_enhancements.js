/**
 * OSUS Properties - Premium JavaScript Enhancements
 * Modern ES6+ luxury interactive features for Odoo17
 * =====================================================
 */

(() => {
  "use strict";

  // Modern OSUS Luxury Enhancement Class
  class OSUSEnhancements {
    #observers = new Map();
    #eventListeners = new Map();
    #animationFrame = null;
    #isInitialized = false;

    constructor() {
      this.#init();
    }

    async #init() {
      if (this.#isInitialized) return;

      try {
        await this.#initializeFeatures();
        this.#isInitialized = true;
        console.log("🏆 OSUS Premium Enhancements loaded successfully");
      } catch (error) {
        console.error("❌ OSUS Enhancement initialization failed:", error);
      }
    }

    async #initializeFeatures() {
      const features = [
        this.#initScrollAnimations(),
        this.#initParallaxEffects(),
        this.#initLuxuryHovers(),
        this.#initSmartNavigation(),
        this.#initAdvancedNotifications(),
        this.#initFormEnhancements(),
        this.#initLoadingStates(),
        this.#initThemeToggle(),
        this.#initPerformanceOptimizations(),
      ];

      await Promise.allSettled(features);
    }

    // LUXURY SCROLL ANIMATIONS WITH INTERSECTION OBSERVER
    // ===================================================
    async #initScrollAnimations() {
      const observerOptions = {
        threshold: [0, 0.1, 0.25, 0.5, 0.75, 1],
        rootMargin: "0px 0px -50px 0px",
      };

      const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("revealed");

            // Modern stagger animation with requestAnimationFrame
            const items = entry.target.querySelectorAll(
              ".list-item, .grid-item, .card"
            );
            this.#staggerAnimation(items);
          }
        });
      }, observerOptions);

      this.#observers.set("scroll", scrollObserver);

      // Observe all scroll reveal elements
      document.querySelectorAll(".osus-scroll-reveal").forEach((el) => {
        scrollObserver.observe(el);
      });

      // Enhanced scroll progress with modern CSS properties
      this.#createScrollProgress();
    }

    #staggerAnimation(items) {
      items.forEach((item, index) => {
        this.#animationFrame = requestAnimationFrame(() => {
          setTimeout(() => {
            item.classList.add("osus-fade-in");
          }, index * 100);
        });
      });
    }

    #createScrollProgress() {
      if (document.querySelector(".osus-scroll-progress")) return;

      const progressBar = this.#createElement("div", {
        className: "osus-scroll-progress",
        innerHTML: '<div class="progress-fill"></div>',
      });

      document.body.appendChild(progressBar);
      const progressFill = progressBar.querySelector(".progress-fill");

      const updateProgress = () => {
        const { scrollTop, scrollHeight, clientHeight } =
          document.documentElement;
        const scrolled = Math.min(
          (scrollTop / (scrollHeight - clientHeight)) * 100,
          100
        );
        progressFill.style.inlineSize = `${scrolled}%`;
      };

      const scrollHandler = this.#throttle(updateProgress, 16);
      this.#addEventListenerTracked(window, "scroll", scrollHandler, {
        passive: true,
      });
      this.#addProgressBarStyles();
    }

    #addProgressBarStyles() {
      if (document.querySelector("#osus-progress-styles")) return;

      const style = this.#createElement("style", {
        id: "osus-progress-styles",
        textContent: `
                    .osus-scroll-progress {
                        position: fixed;
                        inset-block-start: 0;
                        inset-inline: 0;
                        block-size: 4px;
                        z-index: 9999;
                        background: color-mix(in srgb, #4d1a1a 10%, transparent);
                    }
                    .progress-fill {
                        block-size: 100%;
                        background: linear-gradient(135deg, #4d1a1a 0%, #b8a366 100%);
                        transition: inline-size 0.1s ease;
                        inline-size: 0%;
                    }
                `,
      });
      document.head.appendChild(style);
    }

    // MODERN PARALLAX WITH PERFORMANCE OPTIMIZATION
    // =============================================
    async #initParallaxEffects() {
      const parallaxElements = document.querySelectorAll(".osus-parallax");

      if (parallaxElements.length === 0) return;

      // Check for reduced motion preference
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        return;
      }

      let ticking = false;

      const updateParallax = () => {
        const scrollTop = window.pageYOffset;

        parallaxElements.forEach((element) => {
          const rect = element.getBoundingClientRect();
          const speed = parseFloat(element.dataset.speed) || 0.5;
          const yPos = -(scrollTop * speed);

          if (rect.bottom >= 0 && rect.top <= window.innerHeight) {
            element.style.transform = `translate3d(0, ${yPos}px, 0)`;
          }
        });

        ticking = false;
      };

      const requestParallaxUpdate = () => {
        if (!ticking) {
          this.#animationFrame = requestAnimationFrame(updateParallax);
          ticking = true;
        }
      };

      this.#addEventListenerTracked(window, "scroll", requestParallaxUpdate, {
        passive: true,
      });
    }

    // MODERN LUXURY HOVER EFFECTS WITH WEB ANIMATIONS API
    // ===================================================
    async #initLuxuryHovers() {
      // Advanced card hover effects using Web Animations API
      document
        .querySelectorAll(".card, .osus-dashboard-card")
        .forEach((card) => {
          card.addEventListener("mouseenter", (e) => {
            this.#createModernRippleEffect(e);
            this.#animateCardHover(card, true);
          });

          card.addEventListener("mouseleave", () => {
            this.#animateCardHover(card, false);
          });
        });

      // Modern button effects with CSS custom properties
      document
        .querySelectorAll(".btn-primary, .btn-secondary")
        .forEach((btn) => {
          this.#enhanceButton(btn);
        });

      // Enhanced form input focus with modern CSS
      document.querySelectorAll(".form-control, .o_input").forEach((input) => {
        this.#enhanceInput(input);
      });
    }

    #animateCardHover(card, isHover) {
      const transform = isHover
        ? "translateY(-4px) scale(1.02)"
        : "translateY(0) scale(1)";
      const boxShadow = isHover
        ? "0 20px 40px rgba(77, 26, 26, 0.15)"
        : "0 2px 8px rgba(77, 26, 26, 0.08)";

      card.animate(
        [
          { transform: card.style.transform || "translateY(0) scale(1)" },
          { transform },
        ],
        {
          duration: 300,
          easing: "cubic-bezier(0.4, 0, 0.2, 1)",
          fill: "forwards",
        }
      );

      card.style.boxShadow = boxShadow;
    }

    #createModernRippleEffect(e) {
      const element = e.currentTarget;
      const rect = element.getBoundingClientRect();

      const ripple = this.#createElement("span", {
        className: "osus-ripple",
      });

      const diameter = Math.max(element.offsetWidth, element.offsetHeight);
      const radius = diameter / 2;

      Object.assign(ripple.style, {
        width: `${diameter}px`,
        height: `${diameter}px`,
        left: `${e.clientX - rect.left - radius}px`,
        top: `${e.clientY - rect.top - radius}px`,
      });

      // Remove existing ripple
      element.querySelector(".osus-ripple")?.remove();
      element.appendChild(ripple);

      // Animate with Web Animations API
      ripple.animate(
        [
          { transform: "scale(0)", opacity: 0.6 },
          { transform: "scale(4)", opacity: 0 },
        ],
        {
          duration: 600,
          easing: "ease-out",
        }
      ).onfinish = () => ripple.remove();

      this.#addRippleStyles();
    }

    #addRippleStyles() {
      if (document.querySelector("#osus-ripple-style")) return;

      const style = this.#createElement("style", {
        id: "osus-ripple-style",
        textContent: `
                    .osus-ripple {
                        position: absolute;
                        border-radius: 50%;
                        background: color-mix(in srgb, white 30%, transparent);
                        pointer-events: none;
                        z-index: 1;
                    }
                `,
      });
      document.head.appendChild(style);
    }

    #enhanceButton(btn) {
      btn.addEventListener("mouseenter", () => {
        btn.style.setProperty("--osus-hover-scale", "1.05");
        btn.style.transform = "scale(var(--osus-hover-scale, 1))";
      });

      btn.addEventListener("mouseleave", () => {
        btn.style.setProperty("--osus-hover-scale", "1");
        btn.style.transform = "scale(var(--osus-hover-scale, 1))";
      });

      btn.style.transition = "transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)";
    }

    #enhanceInput(input) {
      const parent =
        input.closest(".form-group, .o_field_widget") || input.parentElement;

      input.addEventListener("focus", () => {
        parent.style.setProperty(
          "--osus-focus-ring",
          "0 0 0 3px color-mix(in srgb, #4d1a1a 20%, transparent)"
        );
      });

      input.addEventListener("blur", () => {
        parent.style.removeProperty("--osus-focus-ring");
      });
    }

    // SMART NAVIGATION WITH MODERN APIs
    // =================================
    async #initSmartNavigation() {
      await this.#initAutoHideNavigation();
      await this.#initEnhancedDropdowns();
      await this.#initMobileNavigation();
    }

    async #initAutoHideNavigation() {
      const navbar = document.querySelector(".o_navbar, .osus-main-nav");
      if (!navbar) return;

      let lastScrollY = window.scrollY;
      let isScrolling = false;

      const handleScroll = () => {
        if (!isScrolling) {
          this.#animationFrame = requestAnimationFrame(() => {
            const currentScrollY = window.scrollY;
            const scrollingDown =
              currentScrollY > lastScrollY && currentScrollY > 100;

            navbar.style.transform = scrollingDown
              ? "translateY(-100%)"
              : "translateY(0)";
            lastScrollY = currentScrollY;
            isScrolling = false;
          });
          isScrolling = true;
        }
      };

      this.#addEventListenerTracked(window, "scroll", handleScroll, {
        passive: true,
      });

      // Add CSS for smooth navigation hiding
      this.#addNavigationStyles();
    }

    #addNavigationStyles() {
      const style = this.#createElement("style", {
        textContent: `
                    .o_navbar, .osus-main-nav {
                        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                        will-change: transform;
                    }
                `,
      });
      document.head.appendChild(style);
    }

    async #initEnhancedDropdowns() {
      document.querySelectorAll(".dropdown, .nav-item").forEach((dropdown) => {
        const menu = dropdown.querySelector(".dropdown-menu, .nav-dropdown");
        if (!menu) return;

        let hoverTimeout;

        dropdown.addEventListener("mouseenter", () => {
          clearTimeout(hoverTimeout);
          this.#animateDropdown(menu, true);
        });

        dropdown.addEventListener("mouseleave", () => {
          hoverTimeout = setTimeout(() => {
            this.#animateDropdown(menu, false);
          }, 150);
        });
      });
    }

    #animateDropdown(menu, show) {
      const animation = show
        ? [
            { opacity: 0, transform: "translateY(-10px) scale(0.95)" },
            { opacity: 1, transform: "translateY(0) scale(1)" },
          ]
        : [
            { opacity: 1, transform: "translateY(0) scale(1)" },
            { opacity: 0, transform: "translateY(-10px) scale(0.95)" },
          ];

      menu.animate(animation, {
        duration: 200,
        easing: "cubic-bezier(0.4, 0, 0.2, 1)",
        fill: "forwards",
      });
    }

    async #initMobileNavigation() {
      const mobileToggle = document.querySelector(
        ".nav-mobile-toggle, .o_mobile_menu_toggle"
      );
      const mobileMenu = document.querySelector(".nav-menu, .o_mobile_menu");

      if (!mobileToggle || !mobileMenu) return;

      mobileToggle.addEventListener("click", () => {
        const isOpen = mobileMenu.classList.contains("mobile-open");
        this.#toggleMobileMenu(!isOpen, mobileMenu, mobileToggle);
      });

      // Modern outside click detection with AbortController
      const controller = new AbortController();
      document.addEventListener(
        "click",
        (e) => {
          if (
            !mobileMenu.contains(e.target) &&
            !mobileToggle.contains(e.target)
          ) {
            this.#toggleMobileMenu(false, mobileMenu, mobileToggle);
          }
        },
        { signal: controller.signal }
      );
    }

    #toggleMobileMenu(isOpen, menu, toggle) {
      menu.classList.toggle("mobile-open", isOpen);
      toggle.classList.toggle("active", isOpen);
      document.body.classList.toggle("nav-open", isOpen);

      // Animate hamburger icon
      const hamburger = toggle.querySelector(".hamburger");
      if (hamburger) {
        hamburger.style.transform = isOpen ? "rotate(45deg)" : "rotate(0deg)";
      }
    }

    // ADVANCED NOTIFICATIONS WITH MODERN APIs
    // =======================================
    async #initAdvancedNotifications() {
      this.#createNotificationContainer();
      this.#setupGlobalNotificationAPI();
      this.#observeOdooNotifications();
    }

    #createNotificationContainer() {
      if (document.querySelector(".osus-notifications")) return;

      const container = this.#createElement("div", {
        className: "osus-notifications",
        style: `
                    position: fixed;
                    inset-block-start: 1.25rem;
                    inset-inline-end: 1.25rem;
                    z-index: 10000;
                    max-inline-size: 25rem;
                    pointer-events: none;
                `,
      });
      document.body.appendChild(container);
    }

    #setupGlobalNotificationAPI() {
      window.osusNotify = async (message, type = "info", options = {}) => {
        return this.#showNotification(message, type, options);
      };
    }

    async #showNotification(message, type, options = {}) {
      const { duration = 5000, persistent = false, actions = [] } = options;

      const notification = this.#createElement("div", {
        className: `osus-notification osus-notification-${type}`,
        innerHTML: `
                    <div class="notification-content">
                        <div class="notification-icon" aria-hidden="true">
                            ${this.#getNotificationIcon(type)}
                        </div>
                        <div class="notification-message">${message}</div>
                        <button class="notification-close" aria-label="Close notification">&times;</button>
                    </div>
                    ${
                      !persistent
                        ? '<div class="notification-progress"></div>'
                        : ""
                    }
                `,
      });

      const container = document.querySelector(".osus-notifications");
      container.appendChild(notification);

      // Modern entrance animation
      await this.#animateNotificationEntrance(notification);

      // Setup auto-removal if not persistent
      if (!persistent) {
        this.#setupNotificationTimer(notification, duration);
      }

      // Setup manual close
      this.#setupNotificationClose(notification);

      this.#addNotificationStyles();
      return notification;
    }

    async #animateNotificationEntrance(notification) {
      return notification.animate(
        [
          {
            opacity: 0,
            transform: "translateX(100%) scale(0.8)",
            filter: "blur(4px)",
          },
          {
            opacity: 1,
            transform: "translateX(0) scale(1)",
            filter: "blur(0px)",
          },
        ],
        {
          duration: 400,
          easing: "cubic-bezier(0.25, 0.46, 0.45, 0.94)",
          fill: "forwards",
        }
      ).finished;
    }

    #setupNotificationTimer(notification, duration) {
      const progressBar = notification.querySelector(".notification-progress");
      if (progressBar) {
        progressBar.style.animationDuration = `${duration}ms`;
        progressBar.style.animation = "osus-progress-reduce linear forwards";
      }

      setTimeout(() => {
        this.#removeNotification(notification);
      }, duration);
    }

    #setupNotificationClose(notification) {
      const closeBtn = notification.querySelector(".notification-close");
      closeBtn.addEventListener("click", () => {
        this.#removeNotification(notification);
      });
    }

    async #removeNotification(notification) {
      await notification.animate(
        [
          { opacity: 1, transform: "translateX(0) scale(1)" },
          { opacity: 0, transform: "translateX(100%) scale(0.8)" },
        ],
        {
          duration: 300,
          easing: "cubic-bezier(0.55, 0.06, 0.68, 0.19)",
          fill: "forwards",
        }
      ).finished;

      notification.remove();
    }

    #getNotificationIcon(type) {
      const icons = {
        success: "✓",
        error: "✕",
        warning: "⚠",
        info: "ⓘ",
      };
      return icons[type] || icons.info;
    }

    #observeOdooNotifications() {
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          mutation.addedNodes.forEach((node) => {
            if (
              node.nodeType === 1 &&
              node.classList?.contains("o_notification")
            ) {
              this.#enhanceOdooNotification(node);
            }
          });
        });
      });

      observer.observe(document.body, { childList: true, subtree: true });
      this.#observers.set("notifications", observer);
    }

    #enhanceOdooNotification(notification) {
      notification.style.cssText = `
                background: linear-gradient(135deg, #fff 0%, #fafafa 100%);
                border-inline-start: 4px solid #4d1a1a;
                border-radius: 12px;
                box-shadow: 0 10px 25px color-mix(in srgb, #4d1a1a 15%, transparent);
            `;
    }

    #addNotificationStyles() {
      if (document.querySelector("#osus-notification-styles")) return;

      const style = this.#createElement("style", {
        id: "osus-notification-styles",
        textContent: `
                    .osus-notification {
                        background: white;
                        border-radius: 12px;
                        box-shadow: 0 10px 25px color-mix(in srgb, #4d1a1a 15%, transparent);
                        margin-block-end: 1rem;
                        overflow: hidden;
                        border-inline-start: 4px solid #4d1a1a;
                        pointer-events: auto;
                        backdrop-filter: blur(8px);
                    }
                    .notification-content {
                        padding: 1rem 1.25rem;
                        display: flex;
                        align-items: center;
                    }
                    .notification-icon {
                        inline-size: 1.5rem;
                        block-size: 1.5rem;
                        border-radius: 50%;
                        background: #4d1a1a;
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 0.75rem;
                        font-weight: bold;
                    }
                    .notification-message {
                        flex: 1;
                        margin-inline: 0.75rem;
                        color: #495057;
                        font-weight: 500;
                        line-height: 1.4;
                    }
                    .notification-close {
                        background: none;
                        border: none;
                        font-size: 1.25rem;
                        cursor: pointer;
                        color: #6c757d;
                        padding: 0.25rem;
                        border-radius: 4px;
                        transition: background-color 0.2s ease;
                    }
                    .notification-close:hover {
                        background-color: #f8f9fa;
                    }
                    .notification-progress {
                        block-size: 3px;
                        background: linear-gradient(135deg, #4d1a1a 0%, #b8a366 100%);
                    }
                    @keyframes osus-progress-reduce {
                        from { inline-size: 100%; }
                        to { inline-size: 0%; }
                    }
                `,
      });
      document.head.appendChild(style);
    }

    // MODERN FORM ENHANCEMENTS
    // ========================
    async #initFormEnhancements() {
      await this.#initAutoResize();
      await this.#initFormValidation();
      await this.#initInputFormatting();
      await this.#initFormWizard();
    }

    async #initAutoResize() {
      const textareas = document.querySelectorAll("textarea");

      textareas.forEach((textarea) => {
        const observer = new ResizeObserver(() => {
          textarea.style.height = "auto";
          textarea.style.height = `${textarea.scrollHeight}px`;
        });

        textarea.addEventListener("input", () => {
          textarea.style.height = "auto";
          textarea.style.height = `${textarea.scrollHeight}px`;
        });

        observer.observe(textarea);
      });
    }

    async #initFormValidation() {
      document.querySelectorAll("form").forEach((form) => {
        form.addEventListener("submit", (e) => {
          this.#validateForm(form, e);
        });
      });
    }

    #validateForm(form, event) {
      const inputs = form.querySelectorAll(
        "input[required], textarea[required], select[required]"
      );
      const errors = [];

      inputs.forEach((input) => {
        const value = input.value.trim();
        const fieldName =
          input.getAttribute("name") || input.getAttribute("id") || "Field";

        if (!value) {
          errors.push({ input, message: `${fieldName} is required` });
        } else {
          this.#clearFieldError(input);
        }
      });

      if (errors.length > 0) {
        event.preventDefault();
        errors.forEach(({ input, message }) => {
          this.#showFieldError(input, message);
        });

        // Focus on first error
        errors[0].input.focus();
        window.osusNotify("Please correct the highlighted fields", "error");
      }
    }

    #showFieldError(field, message) {
      this.#clearFieldError(field);

      const errorElement = this.#createElement("div", {
        className: "osus-field-error",
        textContent: message,
        style: `
                    color: #dc3545;
                    font-size: 0.875rem;
                    margin-block-start: 0.25rem;
                    animation: shake 0.5s ease-in-out;
                `,
      });

      field.parentElement.appendChild(errorElement);
      field.style.borderColor = "#dc3545";
    }

    #clearFieldError(field) {
      const errorElement =
        field.parentElement.querySelector(".osus-field-error");
      errorElement?.remove();
      field.style.borderColor = "";
    }

    async #initInputFormatting() {
      // Modern phone number formatting with international support
      document.querySelectorAll('input[type="tel"]').forEach((input) => {
        input.addEventListener("input", this.#formatPhoneNumber.bind(this));
      });

      // Currency formatting with Intl API
      document.querySelectorAll("input[data-currency]").forEach((input) => {
        input.addEventListener("blur", this.#formatCurrency.bind(this));
      });

      // Date formatting
      document.querySelectorAll('input[type="date"]').forEach((input) => {
        input.addEventListener("change", this.#formatDate.bind(this));
      });
    }

    #formatPhoneNumber(e) {
      const input = e.target;
      let value = input.value.replace(/\D/g, "");

      if (value.length >= 6) {
        value = value.replace(/(\d{3})(\d{3})(\d{4})/, "($1) $2-$3");
      } else if (value.length >= 3) {
        value = value.replace(/(\d{3})(\d{0,3})/, "($1) $2");
      }

      input.value = value;
    }

    #formatCurrency(e) {
      const input = e.target;
      const currency = input.dataset.currency || "USD";
      const value = parseFloat(input.value.replace(/[^\d.-]/g, ""));

      if (!isNaN(value)) {
        input.value = new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: currency,
          minimumFractionDigits: 0,
          maximumFractionDigits: 2,
        }).format(value);
      }
    }

    #formatDate(e) {
      const input = e.target;
      const date = new Date(input.value);

      if (!isNaN(date.getTime())) {
        input.setAttribute(
          "data-formatted",
          new Intl.DateTimeFormat("en-US", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          }).format(date)
        );
      }
    }

    async #initFormWizard() {
      document.querySelectorAll(".form-wizard").forEach((wizard) => {
        this.#setupWizard(wizard);
      });
    }

    #setupWizard(wizard) {
      const steps = wizard.querySelectorAll(".wizard-step");
      const nextBtns = wizard.querySelectorAll(".btn-next");
      const prevBtns = wizard.querySelectorAll(".btn-prev");
      let currentStep = 0;

      const showStep = async (step) => {
        steps.forEach((s, index) => {
          s.classList.toggle("active", index === step);
          s.classList.toggle("completed", index < step);
        });

        // Animate step transition
        if (steps[step]) {
          await steps[step].animate(
            [
              { opacity: 0, transform: "translateX(20px)" },
              { opacity: 1, transform: "translateX(0)" },
            ],
            {
              duration: 300,
              easing: "cubic-bezier(0.4, 0, 0.2, 1)",
            }
          ).finished;
        }
      };

      nextBtns.forEach((btn) => {
        btn.addEventListener("click", async () => {
          if (currentStep < steps.length - 1) {
            currentStep++;
            await showStep(currentStep);
          }
        });
      });

      prevBtns.forEach((btn) => {
        btn.addEventListener("click", async () => {
          if (currentStep > 0) {
            currentStep--;
            await showStep(currentStep);
          }
        });
      });

      showStep(0);
    }

    // MODERN LOADING STATES WITH WEB ANIMATIONS
    // =========================================
    async #initLoadingStates() {
      window.osusLoading = {
        show: (message = "Loading...") => this.#showLoading(message),
        hide: () => this.#hideLoading(),
        progress: (value) => this.#updateProgress(value),
      };

      this.#interceptNetworkRequests();
    }

    async #showLoading(message) {
      let overlay = document.querySelector(".osus-loading-overlay");

      if (!overlay) {
        overlay = this.#createElement("div", {
          className: "osus-loading-overlay",
          innerHTML: `
                        <div class="loading-content">
                            <div class="osus-spinner osus-spinner-lg"></div>
                            <div class="loading-message">${message}</div>
                            <div class="loading-progress">
                                <div class="progress-bar"></div>
                            </div>
                        </div>
                    `,
        });
        document.body.appendChild(overlay);
        this.#addLoadingStyles();
      } else {
        overlay.querySelector(".loading-message").textContent = message;
      }

      // Modern backdrop blur with CSS custom properties
      overlay.style.setProperty("--backdrop-opacity", "1");
      overlay.style.setProperty("--backdrop-blur", "8px");
    }

    async #hideLoading() {
      const overlay = document.querySelector(".osus-loading-overlay");
      if (!overlay) return;

      await overlay.animate(
        [
          { opacity: 1, backdropFilter: "blur(8px)" },
          { opacity: 0, backdropFilter: "blur(0px)" },
        ],
        {
          duration: 300,
          easing: "cubic-bezier(0.4, 0, 0.2, 1)",
        }
      ).finished;

      overlay.remove();
    }

    #updateProgress(value) {
      const progressBar = document.querySelector(
        ".osus-loading-overlay .progress-bar"
      );
      if (progressBar) {
        progressBar.style.transform = `scaleX(${value / 100})`;
      }
    }

    #interceptNetworkRequests() {
      // Modern fetch interception with proper error handling
      const originalFetch = window.fetch;
      window.fetch = async (...args) => {
        this.#showLoading("Loading...");
        try {
          const response = await originalFetch(...args);
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          return response;
        } catch (error) {
          window.osusNotify(`Network error: ${error.message}`, "error");
          throw error;
        } finally {
          this.#hideLoading();
        }
      };

      // Modern XMLHttpRequest interception
      const originalXHR = window.XMLHttpRequest;
      window.XMLHttpRequest = class extends originalXHR {
        open(...args) {
          this.addEventListener("loadstart", () => this.#showLoading());
          this.addEventListener("loadend", () => this.#hideLoading());
          super.open(...args);
        }
      };
    }

    #addLoadingStyles() {
      if (document.querySelector("#osus-loading-styles")) return;

      const style = this.#createElement("style", {
        id: "osus-loading-styles",
        textContent: `
                    .osus-loading-overlay {
                        position: fixed;
                        inset: 0;
                        background: color-mix(in srgb, #4d1a1a 10%, transparent);
                        backdrop-filter: blur(var(--backdrop-blur, 0px));
                        z-index: 99999;
                        display: grid;
                        place-items: center;
                        opacity: var(--backdrop-opacity, 0);
                        transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    }
                    .loading-content {
                        background: white;
                        padding: 2.5rem;
                        border-radius: 1rem;
                        box-shadow: 0 20px 40px color-mix(in srgb, #4d1a1a 20%, transparent);
                        text-align: center;
                        max-inline-size: 18.75rem;
                        animation: float 3s ease-in-out infinite;
                    }
                    .loading-message {
                        margin-block-start: 1.25rem;
                        color: #495057;
                        font-weight: 600;
                        font-size: 1rem;
                    }
                    .loading-progress {
                        margin-block-start: 1rem;
                        block-size: 4px;
                        background: #f8f9fa;
                        border-radius: 2px;
                        overflow: hidden;
                    }
                    .progress-bar {
                        block-size: 100%;
                        background: linear-gradient(135deg, #4d1a1a 0%, #b8a366 100%);
                        transform: scaleX(0);
                        transform-origin: left;
                        transition: transform 0.3s ease;
                    }
                    @keyframes float {
                        0%, 100% { transform: translateY(0px); }
                        50% { transform: translateY(-10px); }
                    }
                `,
      });
      document.head.appendChild(style);
    }

    // MODERN THEME TOGGLE WITH CSS CUSTOM PROPERTIES
    // ==============================================
    async #initThemeToggle() {
      const themeToggle = this.#createElement("button", {
        className: "osus-theme-toggle",
        innerHTML: "🌙",
        "aria-label": "Toggle dark mode",
      });
      document.body.appendChild(themeToggle);

      // Load saved theme with modern localStorage
      const savedTheme = localStorage.getItem("osus-theme") ?? "light";
      this.#setTheme(savedTheme);

      themeToggle.addEventListener("click", () => {
        const currentTheme =
          document.documentElement.getAttribute("data-theme") || "light";
        const newTheme = currentTheme === "light" ? "dark" : "light";
        this.#setTheme(newTheme);
        localStorage.setItem("osus-theme", newTheme);
      });

      this.#addThemeStyles();
    }

    #setTheme(theme) {
      const toggle = document.querySelector(".osus-theme-toggle");
      document.documentElement.setAttribute("data-theme", theme);

      if (toggle) {
        toggle.innerHTML = theme === "dark" ? "☀️" : "🌙";
        toggle.setAttribute(
          "aria-label",
          `Switch to ${theme === "dark" ? "light" : "dark"} mode`
        );
      }
    }

    #addThemeStyles() {
      const style = this.#createElement("style", {
        textContent: `
                    :root {
                        --osus-bg-primary: light-dark(#ffffff, #1a1a1a);
                        --osus-bg-secondary: light-dark(#f8f9fa, #2d2d2d);
                        --osus-text-primary: light-dark(#212529, #e0e0e0);
                        --osus-text-secondary: light-dark(#6c757d, #a0a0a0);
                        --osus-border-color: light-dark(#dee2e6, #404040);
                    }
                    
                    .osus-theme-toggle {
                        position: fixed;
                        inset-block-end: 1.25rem;
                        inset-inline-start: 1.25rem;
                        inline-size: 3.125rem;
                        block-size: 3.125rem;
                        border-radius: 50%;
                        border: none;
                        background: linear-gradient(135deg, #4d1a1a 0%, #b8a366 100%);
                        color: white;
                        font-size: 1.25rem;
                        cursor: pointer;
                        box-shadow: 0 10px 25px color-mix(in srgb, #4d1a1a 30%, transparent);
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                        z-index: 1000;
                    }
                    .osus-theme-toggle:hover {
                        transform: scale(1.1) rotate(15deg);
                        box-shadow: 0 15px 35px color-mix(in srgb, #4d1a1a 40%, transparent);
                    }
                    
                    [data-theme="dark"] .o_content,
                    [data-theme="dark"] .card,
                    [data-theme="dark"] .osus-dashboard-card {
                        background: var(--osus-bg-secondary);
                        color: var(--osus-text-primary);
                        border-color: var(--osus-border-color);
                    }
                    [data-theme="dark"] .o_web_client {
                        background: var(--osus-bg-primary);
                    }
                `,
      });
      document.head.appendChild(style);
    }

    // PERFORMANCE OPTIMIZATIONS WITH MODERN APIs
    // ==========================================
    async #initPerformanceOptimizations() {
      await this.#initLazyLoading();
      await this.#initOptimizedResize();
      await this.#initIntersectionOptimizations();
      await this.#initMemoryManagement();
    }

    async #initLazyLoading() {
      // Modern native lazy loading with fallback
      const images = document.querySelectorAll("img[data-src]");

      if ("loading" in HTMLImageElement.prototype) {
        // Use native lazy loading
        images.forEach((img) => {
          img.loading = "lazy";
          img.src = img.dataset.src;
          img.classList.add("osus-fade-in");
        });
      } else {
        // Fallback to Intersection Observer
        const imageObserver = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add("osus-fade-in");
                imageObserver.unobserve(img);
              }
            });
          },
          { rootMargin: "50px" }
        );

        images.forEach((img) => imageObserver.observe(img));
        this.#observers.set("lazy-images", imageObserver);
      }
    }

    async #initOptimizedResize() {
      // Modern ResizeObserver for optimal resize handling
      if ("ResizeObserver" in window) {
        const resizeObserver = new ResizeObserver(
          this.#throttle((entries) => {
            this.#handleResize(entries);
          }, 250)
        );

        resizeObserver.observe(document.body);
        this.#observers.set("resize", resizeObserver);
      } else {
        // Fallback to window resize
        this.#addEventListenerTracked(
          window,
          "resize",
          this.#throttle(() => this.#handleResize(), 250)
        );
      }
    }

    #handleResize(entries = []) {
      // Update responsive elements
      this.#updateResponsiveElements();

      // Reset parallax elements
      document.querySelectorAll(".osus-parallax").forEach((el) => {
        el.style.transform = "translate3d(0, 0, 0)";
      });

      // Dispatch custom resize event
      window.dispatchEvent(
        new CustomEvent("osus:resize", {
          detail: { entries },
        })
      );
    }

    #updateResponsiveElements() {
      const breakpoints = {
        mobile: window.innerWidth < 768,
        tablet: window.innerWidth >= 768 && window.innerWidth < 1024,
        desktop: window.innerWidth >= 1024,
      };

      Object.entries(breakpoints).forEach(([name, matches]) => {
        document.body.classList.toggle(`osus-${name}`, matches);
      });
    }

    async #initIntersectionOptimizations() {
      // Pause animations when not visible
      const visibilityObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            const element = entry.target;
            if (entry.isIntersecting) {
              element.style.animationPlayState = "running";
            } else {
              element.style.animationPlayState = "paused";
            }
          });
        },
        { threshold: 0 }
      );

      document
        .querySelectorAll('[class*="osus-"], .card, .btn')
        .forEach((el) => {
          visibilityObserver.observe(el);
        });

      this.#observers.set("visibility", visibilityObserver);
    }

    async #initMemoryManagement() {
      // Cleanup on page unload
      this.#addEventListenerTracked(window, "beforeunload", () => {
        this.#cleanup();
      });

      // Periodic cleanup for long sessions
      this.#cleanupInterval = setInterval(() => {
        this.#performPeriodicCleanup();
      }, 5 * 60 * 1000); // Every 5 minutes
    }

    #performPeriodicCleanup() {
      // Remove old notifications
      const notifications = document.querySelectorAll(".osus-notification");
      if (notifications.length > 5) {
        Array.from(notifications)
          .slice(0, -5)
          .forEach((notification) => notification.remove());
      }

      // Clean up old ripple effects
      document.querySelectorAll(".osus-ripple").forEach((ripple) => {
        ripple.remove();
      });

      // Garbage collect unused observers
      this.#observers.forEach((observer, key) => {
        if (!observer || typeof observer.disconnect !== "function") {
          this.#observers.delete(key);
        }
      });
    }

    #cleanup() {
      // Cancel any pending animation frames
      if (this.#animationFrame) {
        cancelAnimationFrame(this.#animationFrame);
      }

      // Clear intervals
      if (this.#cleanupInterval) {
        clearInterval(this.#cleanupInterval);
      }

      // Disconnect all observers
      this.#observers.forEach((observer) => {
        observer?.disconnect?.();
      });
      this.#observers.clear();

      // Remove tracked event listeners
      this.#eventListeners.forEach(({ element, event, handler }) => {
        element?.removeEventListener?.(event, handler);
      });
      this.#eventListeners.clear();
    }

    // UTILITY METHODS
    // ===============

    #createElement(tag, attributes = {}) {
      const element = document.createElement(tag);
      Object.entries(attributes).forEach(([key, value]) => {
        if (key === "style" || key === "textContent" || key === "innerHTML") {
          element[key] = value;
        } else {
          element.setAttribute(key, value);
        }
      });
      return element;
    }

    #addEventListenerTracked(element, event, handler, options = {}) {
      element.addEventListener(event, handler, options);
      this.#eventListeners.set(`${event}-${Date.now()}`, {
        element,
        event,
        handler,
      });
    }

    #throttle(func, delay) {
      let timeoutId;
      let lastExecTime = 0;

      return (...args) => {
        const currentTime = performance.now();

        if (currentTime - lastExecTime > delay) {
          func.apply(this, args);
          lastExecTime = currentTime;
        } else {
          clearTimeout(timeoutId);
          timeoutId = setTimeout(() => {
            func.apply(this, args);
            lastExecTime = performance.now();
          }, delay - (currentTime - lastExecTime));
        }
      };
    }

    #debounce(func, delay) {
      let timeoutId;
      return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
      };
    }
  }

  // MODERN UTILITY FUNCTIONS
  // ========================

  // Smooth scroll with modern API
  window.osusScrollTo = async (target, options = {}) => {
    const element =
      typeof target === "string" ? document.querySelector(target) : target;
    if (!element) return false;

    const { offset = 0, behavior = "smooth" } = options;
    const top = element.offsetTop - offset;

    try {
      await new Promise((resolve) => {
        window.scrollTo({ top, behavior });
        // Modern scroll detection
        const checkScroll = () => {
          if (Math.abs(window.scrollY - top) < 1) {
            resolve();
          } else {
            requestAnimationFrame(checkScroll);
          }
        };
        checkScroll();
      });
      return true;
    } catch (error) {
      console.error("Scroll failed:", error);
      return false;
    }
  };

  // Modern currency formatting with regional support
  window.osusFormatCurrency = (amount, options = {}) => {
    const {
      currency = "USD",
      locale = "en-US",
      minimumFractionDigits = 0,
      maximumFractionDigits = 2,
    } = options;

    try {
      return new Intl.NumberFormat(locale, {
        style: "currency",
        currency,
        minimumFractionDigits,
        maximumFractionDigits,
      }).format(amount);
    } catch (error) {
      console.error("Currency formatting failed:", error);
      return `$${amount}`;
    }
  };

  // Modern animated counter with Web Animations API
  window.osusAnimateNumber = async (element, start, end, options = {}) => {
    const {
      duration = 2000,
      easing = "ease-out",
      formatter = (value) => Math.round(value).toLocaleString(),
    } = options;

    if (!element) return false;

    try {
      const range = end - start;
      const startTime = performance.now();

      return new Promise((resolve) => {
        const animate = (currentTime) => {
          const elapsed = currentTime - startTime;
          const progress = Math.min(elapsed / duration, 1);

          // Easing function
          const easedProgress =
            progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
          const current = start + range * easedProgress;

          element.textContent = formatter(current);

          if (progress < 1) {
            requestAnimationFrame(animate);
          } else {
            resolve();
          }
        };

        requestAnimationFrame(animate);
      });
    } catch (error) {
      console.error("Number animation failed:", error);
      element.textContent = formatter(end);
      return false;
    }
  };

  // Modern date formatting
  window.osusFormatDate = (date, options = {}) => {
    const {
      locale = "en-US",
      style = "medium", // short, medium, long, full
    } = options;

    const dateObj = new Date(date);
    if (isNaN(dateObj.getTime())) return "Invalid Date";

    const formatOptions = {
      short: { dateStyle: "short" },
      medium: { dateStyle: "medium" },
      long: { dateStyle: "long" },
      full: { dateStyle: "full" },
    };

    try {
      return new Intl.DateTimeFormat(locale, formatOptions[style]).format(
        dateObj
      );
    } catch (error) {
      console.error("Date formatting failed:", error);
      return dateObj.toLocaleDateString();
    }
  };

  // MODERN INITIALIZATION WITH PROPER ERROR HANDLING
  // ================================================

  const initializeOSUSEnhancements = async () => {
    try {
      // Wait for critical resources
      await Promise.all([
        document.fonts.ready,
        new Promise((resolve) => {
          if (document.readyState === "complete") {
            resolve();
          } else {
            window.addEventListener("load", resolve, { once: true });
          }
        }),
      ]);

      // Initialize enhancements
      window.osusEnhancements = new OSUSEnhancements();

      // Set up global error handling
      window.addEventListener("error", (event) => {
        console.error("OSUS Enhancement Error:", event.error);
        if (window.osusNotify) {
          window.osusNotify("An unexpected error occurred", "error");
        }
      });

      // Performance monitoring
      if ("PerformanceObserver" in window) {
        const observer = new PerformanceObserver((list) => {
          list.getEntries().forEach((entry) => {
            if (entry.entryType === "navigation" && entry.loadEventEnd > 0) {
              console.log(
                `🚀 OSUS Page loaded in ${Math.round(entry.loadEventEnd)}ms`
              );
            }
          });
        });
        observer.observe({ entryTypes: ["navigation"] });
      }
    } catch (error) {
      console.error("Failed to initialize OSUS Enhancements:", error);
    }
  };

  // Initialize based on document state
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeOSUSEnhancements, {
      once: true,
    });
  } else {
    initializeOSUSEnhancements();
  }

  // Modern Odoo integration with proper lifecycle management
  const setupOdooIntegration = () => {
    // Use modern MutationObserver with better performance
    const observerConfig = {
      childList: true,
      subtree: true,
      attributeFilter: ["class", "data-*"],
    };

    const odooObserver = new MutationObserver((mutations) => {
      const hasRelevantChanges = mutations.some(
        (mutation) =>
          mutation.type === "childList" && mutation.addedNodes.length > 0
      );

      if (hasRelevantChanges && window.osusEnhancements) {
        // Debounce re-initialization
        clearTimeout(window.osusReinitTimeout);
        window.osusReinitTimeout = setTimeout(() => {
          window.osusEnhancements.initLuxuryHovers?.();
          window.osusEnhancements.initFormEnhancements?.();
        }, 100);
      }
    });

    // Observe Odoo's main areas
    const targetSelectors = [
      ".o_content",
      ".o_web_client",
      ".o_action_manager",
    ];
    targetSelectors.forEach((selector) => {
      const element = document.querySelector(selector);
      if (element) {
        odooObserver.observe(element, observerConfig);
      }
    });

    // Cleanup observer on page unload
    window.addEventListener(
      "beforeunload",
      () => {
        odooObserver.disconnect();
      },
      { once: true }
    );
  };

  // Set up Odoo integration after initialization
  document.addEventListener("DOMContentLoaded", setupOdooIntegration, {
    once: true,
  });
})();
