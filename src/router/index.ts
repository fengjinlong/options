import { createRouter, createWebHistory } from "vue-router";
import StrategyList from "../components/StrategyList.vue";
import OptionCalendarChart from "../components/OptionCalendarChart.vue";
import SolVolatility from "../views/SolVolatility.vue";
import CmcVolatility from "../views/CmcVolatility.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: StrategyList,
    },
    {
      path: "/calendar-call",
      name: "calendar-call",
      component: OptionCalendarChart,
    },
    {
      path: "/sol-volatility",
      name: "sol-volatility",
      component: SolVolatility,
    },
    {
      path: "/cmc-volatility",
      name: "cmc-volatility",
      component: CmcVolatility,
    },
  ],
});

export default router;
