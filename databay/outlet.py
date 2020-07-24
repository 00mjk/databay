"""
.. seealso:: :any:`Inlet` representing the corresponding input of the data stream.
"""
import asyncio
import threading
from abc import ABC, abstractmethod
from typing import List

from databay import Record
from databay.errors import ImplementationError

class Outlet(ABC):
    """
    Abstract class representing an output of the data stream.
    """

    def __init__(self):
        ""
        self._active = False

        # if not asyncio.iscoroutinefunction(self.push):
        #     raise ImplementationError('Outlet.push() function must be a coroutine. Fix by adding \'async\' keyword.')
        self._uses_coroutine = asyncio.iscoroutinefunction(self.push)

        self._thread_lock = threading.Lock()


    async def _push(self, records:List[Record], update):
        if self._uses_coroutine:
            rv = await self.push(records, update)
        else:
            rv = self.push(records, update)

    @abstractmethod
    async def push(self, records:List[Record], update):
        """
        Push received data.

        Override this method to define how this outlet will handle received data.

        :type records: list[:any:`Record`]
        :param records: List of records generated by inlets. Each top-level element of this array corresponds to one inlet that successfully returned data. Note that inlets could return arrays too, making this a nested array.

        :type update: :any:`Update`
        :param update: Update object representing the particular Link update run.
        """

        raise NotImplementedError()

    def try_start(self):
        should_on_start = False

        with self._thread_lock:
            if not self._active:
                self._active = True
                should_on_start = True

        if should_on_start:
            self.on_start()

    def on_start(self):
        """
        Called once per outlet just before the governing planner is about to start.

        Override this method to provide starting functionality on this outlet.
        """

        pass

    def try_shutdown(self):
        should_on_shutdown = False

        with self._thread_lock:
            if self._active:
                self._active = False
                should_on_shutdown = True

        if should_on_shutdown:
            self.on_shutdown()

    def on_shutdown(self):
        """
        Called once per outlet just after the governing planner has shutdown.

        Override this method to provide shutdown functionality on this outlet.
        """

        pass

    @property
    def active(self):
        """
        Whether this outlet is active and ready to push. This variable is set by
        the governing link to :code:`True` on start and to :code:`False` on shutdown.
        |default| :code:`False`

        :rtype: :class:`bool`
        """

        return self._active

    # @active.setter
    # def active(self, active):
    #     self._active = active

    def __repr__(self):
        return '%s()' % (self.__class__.__name__)
