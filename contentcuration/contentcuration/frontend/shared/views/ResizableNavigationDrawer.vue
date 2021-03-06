<template>

  <VNavigationDrawer
    ref="drawer"
    v-model="open"
    v-bind="$attrs"
    :width="drawerWidth"
    :right="isRight"
    :temporary="temporary"
    :class="{
      'drawer-right': isRight,
      'drawer-left': !isRight,
      dragging,
      draggable: !temporary
    }"
  >
    <div class="drawer-contents" @scroll="e => $emit('scroll', e)">
      <slot></slot>
    </div>
  </VNavigationDrawer>

</template>

<script>

  export default {
    name: 'ResizableNavigationDrawer',
    props: {
      value: {
        type: Boolean,
        default: true,
      },
      minWidth: {
        type: Number,
        default: 10,
      },
      maxWidth: {
        type: Number,
        default: window.innerWidth - 100,
      },
      localName: {
        type: String,
        required: true,
      },
      right: {
        type: Boolean,
        default: false,
      },
      temporary: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        dragging: false,
        width: 300,
      };
    },
    computed: {
      open: {
        get() {
          return this.value;
        },
        set(value) {
          this.$emit('input', value);
        },
      },
      drawerWidth() {
        return this.temporary ? this.maxWidth : this.width;
      },
      drawerElement() {
        return this.$refs.drawer.$el;
      },
      localStorageName() {
        return this.localName + '-drawer-width';
      },
      isRight() {
        return this.$isRTL ? !this.right : this.right;
      },
    },
    beforeMount() {
      this.width = `${this.getWidth()}px`;
    },
    mounted() {
      this.$nextTick(() => {
        const drawerBorder = this.drawerElement.querySelector('.v-navigation-drawer__border');
        drawerBorder.addEventListener('mousedown', this.handleMouseDown, false);
        document.addEventListener('mouseup', this.handleMouseUp, false);
      });
    },
    methods: {
      // @public
      getWidth() {
        const width = localStorage[this.localStorageName] || this.width || this.minWidth;
        return Number(String(width).replace('px', ''));
      },
      resize(e) {
        document.body.style.cursor = 'col-resize';
        let offset = this.isRight ? window.innerWidth - e.clientX : e.clientX;
        let width = Math.min(Math.max(this.minWidth, offset), this.maxWidth);
        this.drawerElement.style.width = localStorage[this.localStorageName] = width + 'px';
        this.$emit('resize', width);
      },
      handleMouseDown(event) {
        if (this.temporary) {
          return;
        }

        // Don't select items on drag
        event.stopPropagation();
        event.preventDefault();

        this.dragging = true;

        document.body.style.pointerEvents = 'none';
        document.querySelectorAll('iframe, embed, video').forEach(iframe => {
          iframe.style.pointerEvents = 'none';
        });

        if (event.offsetX < 12) {
          this.drawerElement.style.transition = 'initial';
          document.addEventListener('mousemove', this.resize, false);
        }
      },
      handleMouseUp() {
        if (this.temporary) {
          return;
        }

        this.drawerElement.style.transition = '';
        this.width = this.drawerElement.style.width;

        this.dragging = false;

        document.body.style.cursor = '';
        document.body.style.pointerEvents = 'unset';
        document.querySelectorAll('iframe, embed, video').forEach(iframe => {
          iframe.style.pointerEvents = 'unset';
        });
        document.removeEventListener('mousemove', this.resize, false);
      },
    },
    $trs: {},
  };

</script>

<style lang="less" scoped>

  /*! rtl:begin:ignore */
  .drawer-left {
    right: auto;
    /deep/ .v-navigation-drawer__border {
      margin-left: 3px;
      border-right: 1px solid var(--v-grey-lighten4);
    }
  }
  .drawer-right {
    left: auto;
    /deep/ .v-navigation-drawer__border {
      margin-right: 3px;
      border-left: 1px solid var(--v-grey-lighten4);
    }
  }

  /*! rtl:end:ignore */

  .draggable /deep/ .v-navigation-drawer__border {
    width: 3px;
    height: 100%;
    cursor: col-resize;
    background: transparent !important;
    transition: background 0.2s ease;
    &:hover,
    .dragging & {
      background: var(--v-secondary-base) !important;
    }
  }

  .drawer-contents {
    width: 100%;
    height: inherit;
    overflow: auto;
  }

</style>
