from django.conf import settings
from django.http import Http404

from .bots import BOT_USER_AGENTS


class PrerenderBotMiddleware:
    def __init__(self, get_response):
        self.BOT_USER_AGENTS = BOT_USER_AGENTS
        self.get_response = get_response

    def is_bot(self, user_agent):
        # Check if the user-agent matches any bot
        return any(bot in user_agent for bot in self.BOT_USER_AGENTS)

    def __call__(self, request):
        if "/prerender" in request.path:
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            # if not settings.DEBUG:
            #     if not self.is_bot(user_agent):
            #         raise Http404("Page not found.")

        return self.get_response(request)
