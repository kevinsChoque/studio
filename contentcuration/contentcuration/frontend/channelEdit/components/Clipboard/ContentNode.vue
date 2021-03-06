<template>

  <VListGroup
    v-model="open"
    append-icon="arrow_drop_down"
    class="parent-item"
    lazy
    sub-group
  >
    <template v-slot:activator>
      <VHover>
        <ContextMenu slot-scope="{ hover }">
          <VListTile
            v-if="contentNode"
            class="content-item py-1"
            :class="{hover, selected}"
            :style="{'padding-left': indentPadding}"
          >
            <VListTileAction class="action-col">
              <Checkbox
                ref="checkbox"
                class="mt-0 pt-0"
                :value="selected"
                :indeterminate="indeterminate"
                @click.stop.prevent="goNextSelectionState"
              />
            </VListTileAction>
            <div
              class="thumbnail-col py-2"
            >
              <Thumbnail
                v-bind="thumbnailAttrs"
                :isEmpty="contentNode.resource_count === 0"
                compact
              />
            </div>

            <template v-if="contentNode.kind === 'topic'">
              <VListTileContent class="description-col pl-2 shrink">
                <VListTileTitle class="text-truncate" :class="getTitleClass(contentNode)">
                  {{ getTitle(contentNode) }}
                </VListTileTitle>
              </VListTileContent>
              <VListTileAction style="min-width: unset;" class="px-3">
                <div class="badge caption font-weight-bold">
                  {{ contentNode.resource_count }}
                </div>
              </VListTileAction>
              <!-- Custom placement of dropdown indicator -->
              <VListTileAction
                class="v-list__group__header__append-icon action-col px-1"
              >
                <Icon>arrow_drop_down</Icon>
              </VListTileAction>
              <VSpacer />
            </template>
            <template v-else>
              <VListTileContent class="description-col pa-2" @click="goNextSelectionState">
                <VListTileTitle class="text-truncate" :class="getTitleClass(contentNode)">
                  {{ getTitle(contentNode) }}
                </VListTileTitle>
              </VListTileContent>
            </template>

            <VListTileAction class="action-col option-col" :aria-hidden="!hover">
              <VMenu offset-y left>
                <template #activator="{ on }">
                  <VBtn
                    small
                    icon
                    flat
                    class="ma-0"
                    v-on="on"
                    @click.stop
                  >
                    <Icon>more_horiz</Icon>
                  </VBtn>
                </template>

                <ContentNodeOptions :nodeId="nodeId" :ancestorId="ancestorId" />
              </VMenu>
            </VListTileAction>
          </VListTile>
          <template v-if="contentNode" #menu>
            <ContentNodeOptions :nodeId="nodeId" :ancestorId="ancestorId" />
          </template>
        </ContextMenu>
      </VHover>
    </template>

    <transition-group>
      <ContentNode
        v-for="child in children"
        :key="child.id"
        :nodeId="child.id"
        :level="level + 1"
        :ancestorId="childAncestorId"
      />
    </transition-group>

  </VListGroup>

</template>
<script>

  import ContentNodeOptions from './ContentNodeOptions';
  import clipboardMixin, { parentMixin } from './mixins';
  import Checkbox from 'shared/views/form/Checkbox';
  import Thumbnail from 'shared/views/files/Thumbnail';
  import ContextMenu from 'shared/views/ContextMenu';
  import { titleMixin } from 'shared/mixins';

  export default {
    name: 'ContentNode',
    components: {
      Checkbox,
      ContentNodeOptions,
      Thumbnail,
      ContextMenu,
    },
    mixins: [clipboardMixin, parentMixin, titleMixin],
    data() {
      return {
        open: false,
      };
    },
    computed: {
      thumbnailAttrs() {
        if (this.contentNode) {
          const {
            title,
            kind,
            thumbnail_src: src,
            thumbnail_encoding: encoding,
          } = this.contentNode;
          return { title, kind, src, encoding };
        }
        return {};
      },
    },
    mounted() {
      // Prefetch content node data. Since we're using `lazy` with the
      // nested VListGroup, this prefetches one level at a time!
      if (this.contentNode.total_count > 0) {
        this.loadClipboardNodes({ parent: this.nodeId, ancestorId: this.childAncestorId });
      }
    },
  };

</script>
<style lang="less" scoped>

  .content-item,
  .v-list__tile {
    width: 100%;
    max-width: 100%;
    cursor: pointer;
    transition: background-color ease 0.3s;
  }

  .parent-item,
  .v-list__tile {
    width: 100%;
    max-width: 100%;
  }

  /deep/ .v-list__group__header .v-list__group__header__prepend-icon {
    display: none;
  }

  .badge {
    top: 0;
    width: max-content;
    min-width: 22px;
    padding: 0 3px;
    color: white;
    text-align: center;
    background-color: var(--v-primary-base);
    border-radius: 3px;
  }

  .content-item:hover {
    background: #eeeeee;
  }

  /deep/ .action-col,
  .thumbnail-col {
    flex-shrink: 0;
    min-width: 24px;
  }

  .option-col {
    opacity: 0;
    transition: opacity ease 0.3s;

    .content-item.selected &,
    .content-item.hover & {
      opacity: 1;
    }
  }

  /deep/ .v-list__tile {
    padding-left: 11px;
  }

  /deep/ .v-list__tile__title {
    height: auto;
  }

  /deep/ .text-truncate {
    /* fix clipping of dangling characters */
    line-height: 1.3 !important;
  }

</style>
