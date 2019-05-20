import Vue from 'vue';
import Vuetify from 'vuetify';
import colors from 'vuetify/es5/util/colors';
import Sandbox from '../sandbox/Sandbox.vue';

var VueIntl = require('vue-intl');

require('vuetify/dist/vuetify.min.css');
require('../../less/styles.less');

require('utils/translations');
const State = require('edit_channel/state');

var store = require('edit_channel/uploader/vuex/store');

Vue.use(VueIntl);
Vue.use(Vuetify, {
  rtl: window.isRTL,
  theme: {
    primary: colors.blue.base, // @blue-500
    // secondary: colors.red.lighten4, // #FFCDD2
    // accent: colors.indigo.base // #3F51B5
  },
});

if (State.current_channel) {
  State.current_channel.fetch({ async: false });
}

store.commit('edit_modal/SET_NODES', window.nodes);

new Vue({
  el: 'sandbox',
  store,
  ...Sandbox,
});
